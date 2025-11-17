"""
AI Monopoly Game - Pygame UI with smooth animations and dual panels.
Board Panel: Visual game board with player movement and property ownership
AI Panel: Player statistics, AI decision insights, game metrics
"""

import pygame
import sys
import threading
import time
import random
import math
from board_config import (
    BOARD_LAYOUT, PROPERTY_COLORS, PROPERTY_INFO, CORNERS,
    BOARD_WIDTH, BOARD_HEIGHT, CORNER_SIZE, PROPERTY_WIDTH, PROPERTY_HEIGHT,
    COLOR_BACKGROUND, COLOR_CENTER, COLOR_BORDER, COLOR_TEXT,
    COLOR_PLAYER_1, COLOR_PLAYER_2, COLOR_OWNED_BORDER,
    COLOR_PANEL_BG, COLOR_LOG_BG, COLOR_LOG_TEXT,
    FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, FONT_SIZE_TINY
)

# Import game modules
try:
    from property import properties
    from player import Player
    from node import Node
    import tree
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Make sure you're running from the correct directory with all game files present.")
    sys.exit(1)

# Initialize Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Failed to initialize Pygame: {e}")
    print("Please install pygame: pip install pygame")
    sys.exit(1)

class BoardRenderer:
    """Handles all board rendering and layout calculations"""
    
    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.corner_size = CORNER_SIZE
        self.property_width = PROPERTY_WIDTH
        self.property_height = PROPERTY_HEIGHT
        
        # Precompute all 40 board positions
        self.positions = self._compute_board_positions()
    
    def _compute_board_positions(self):
        """Compute pixel coordinates for all 40 board spaces"""
        positions = {}
        corner = self.corner_size
        pw = self.property_width
        ph = self.property_height
        
        # Bottom row: positions 0-10 (GO to JAIL, right to left)
        # Position 0: GO corner (bottom-right)
        positions[0] = {
            'rect': pygame.Rect(self.width - corner, self.height - corner, corner, corner),
            'angle': 0,
            'type': 'corner'
        }
        
        # Positions 1-9: Properties on bottom (right to left)
        # Use corner depth for vertical size so tiles do not overlap corners
        for i in range(1, 10):
            x = self.width - corner - (i * pw)
            positions[i] = {
                'rect': pygame.Rect(int(x), self.height - corner, int(pw), int(corner)),
                'angle': 0,
                'type': 'property'
            }
        
        # Position 10: JAIL corner (bottom-left)
        positions[10] = {
            'rect': pygame.Rect(0, self.height - corner, corner, corner),
            'angle': 0,
            'type': 'corner'
        }
        
        # Left side: positions 11-19 (bottom to top)
        # Use corner depth for horizontal size so tiles do not overlap corners
        for i in range(1, 10):
            y = self.height - corner - (i * ph)
            positions[10 + i] = {
                'rect': pygame.Rect(0, int(y), int(corner), int(ph)),
                'angle': 90,
                'type': 'property'
            }
        
        # Position 20: FREE PARKING corner (top-left)
        positions[20] = {
            'rect': pygame.Rect(0, 0, corner, corner),
            'angle': 0,
            'type': 'corner'
        }
        
        # Top row: positions 21-29 (left to right)
        # Use corner depth for vertical size to align with corners
        for i in range(1, 10):
            x = corner + ((i - 1) * pw)
            positions[20 + i] = {
                'rect': pygame.Rect(int(x), 0, int(pw), int(corner)),
                'angle': 0,
                'type': 'property'
            }
        
        # Position 30: GO TO JAIL corner (top-right)
        positions[30] = {
            'rect': pygame.Rect(self.width - corner, 0, corner, corner),
            'angle': 0,
            'type': 'corner'
        }
        
        # Right side: positions 31-39 (top to bottom)
        # Use corner depth for horizontal size to align with corners
        for i in range(1, 10):
            y = corner + ((i - 1) * ph)
            positions[30 + i] = {
                'rect': pygame.Rect(self.width - corner, int(y), int(corner), int(ph)),
                'angle': 270,
                'type': 'property'
            }
        
        return positions
    
    def get_position(self, board_index):
        """Get pixel rect for a given board position (0-39)"""
        board_index = board_index % 40
        return self.positions.get(board_index, None)


class GameUI:
    """Main Pygame UI with board and AI panels"""
    
    def __init__(self):
        # Window dimensions: board + right panel
        self.board_width = BOARD_WIDTH
        self.board_height = BOARD_HEIGHT
        self.corner_size = CORNER_SIZE
        self.property_width = PROPERTY_WIDTH
        self.property_height = PROPERTY_HEIGHT
        self.panel_width = 420
        self.window_width = self.board_width + self.panel_width + 20
        self.window_height = self.board_height
        
        try:
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption("AI Monopoly Game - Board vs AI Insights")
        except Exception as e:
            print(f"Failed to initialize Pygame display: {e}")
            raise
        
        # Fonts - use system fonts for better readability
        try:
            self.font_title = pygame.font.SysFont('Arial', FONT_SIZE_TITLE, bold=True)
            self.font_large = pygame.font.SysFont('Arial', FONT_SIZE_LARGE, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', FONT_SIZE_MEDIUM, bold=False)
            self.font_small = pygame.font.SysFont('Arial', FONT_SIZE_SMALL, bold=False)
            self.font_tiny = pygame.font.SysFont('Arial', FONT_SIZE_TINY, bold=False)
        except:
            # Fallback to default font
            self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.Font(None, FONT_SIZE_TINY)
        
        # Board renderer
        self.board_renderer = BoardRenderer(self.board_width, self.board_height)
        
        # Game state
        self.players = [Player(0, position=0), Player(1, position=0)]
        self.current_node = None
        self.game_running = False
        self.game_speed = 1.0  # seconds between moves
        self.paused = False
        
        # Animation state
        self.player_animations = {}  # {player_id: {'start_pos': int, 'end_pos': int, 'progress': 0.0}}
        self.last_positions = {0: 0, 1: 0}  # Track previous positions for animation
        
        # Game log
        self.game_log = []
        self.max_log_lines = 200  # Keep more history
        self.log_scroll_offset = 0  # For scrolling
        
        # Control buttons
        self.start_button_rect = None
        self.pause_button_rect = None
        self.reset_button_rect = None
        self.speed_slider_rect = None
        self.speed_slider_handle = None
        self.dragging_slider = False
        
        # Debug info tracking
        self.last_balances = {0: 1500, 1: 1500}
        self.last_utility_scores = {0: 0, 1: 0}
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game thread
        self.game_thread = None
        
        # Lock for thread-safe updates
        import threading
        self.update_lock = threading.Lock()
    
    def render_board(self):
        """Render the game board"""
        # Clear board area with background color
        board_area = pygame.Rect(0, 0, self.board_width, self.board_height)
        pygame.draw.rect(self.screen, COLOR_BACKGROUND, board_area)
        
        # Draw center area with dynamic margins based on board dimensions
        # Margin = corner size + 1 property width + small padding (ensures all 40 spaces visible)
        center_margin = int(self.corner_size + self.property_width + 5)
        center_rect = pygame.Rect(center_margin, center_margin,
                                 self.board_width - 2*center_margin,
                                 self.board_height - 2*center_margin)
        pygame.draw.rect(self.screen, COLOR_CENTER, center_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, center_rect, 3)
        
        # Draw MONOPOLY text in center
        title_text = self.font_title.render("MONOPOLY", True, (139, 0, 0))
        subtitle_text = self.font_large.render("AI BATTLE", True, (75, 0, 0))
        
        title_rect = title_text.get_rect(center=(self.board_width//2, self.board_height//2 - 30))
        subtitle_rect = subtitle_text.get_rect(center=(self.board_width//2, self.board_height//2 + 20))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw all board spaces
        self._draw_properties()
        
        # Draw players
        self._draw_players()
    
    def _draw_properties(self):
        """Draw all 40 properties on the board"""
        for pos_idx in range(40):
            pos_info = self.board_renderer.get_position(pos_idx)
            if pos_info is None:
                continue
            
            space_name = BOARD_LAYOUT[pos_idx]
            space_color = PROPERTY_COLORS.get(space_name, (200, 200, 200))
            
            rect = pos_info['rect']
            
            # Draw space background
            pygame.draw.rect(self.screen, space_color, rect)
            pygame.draw.rect(self.screen, COLOR_BORDER, rect, 2)
            
            # Get property info
            prop_info = PROPERTY_INFO.get(space_name, {})
            
            # Draw property name (centered, with text wrapping)
            if prop_info.get('is_corner', False):
                # Draw corner text centered
                corner_text = self.font_medium.render(space_name, True, COLOR_TEXT)
                text_rect = corner_text.get_rect(center=rect.center)
                self.screen.blit(corner_text, text_rect)
            else:
                # Draw property name with proper orientation
                self._draw_property_text(rect, space_name, pos_info['angle'])
                
                # Draw property value and ownership indicator
                self._draw_property_info(rect, pos_idx, prop_info)
    
    def _draw_property_text(self, rect, name, angle):
        """Draw property name on a space with proper orientation, wrapping to 2 lines if needed"""
        # Split long names into two lines
        display_lines = []
        
        if len(name) > 15:
            words = name.split()
            if len(words) > 1:
                # Try to split intelligently: put words on separate lines
                line1 = words[0]
                line2 = " ".join(words[1:])
                if len(line2) > 12:
                    line2 = line2[:12]
                display_lines = [line1, line2]
            else:
                # Single long word: split in middle
                mid = len(name) // 2
                display_lines = [name[:mid], name[mid:]]
        else:
            display_lines = [name]
        
        # Render text surfaces
        text_surfaces = [self.font_tiny.render(line, True, COLOR_TEXT) for line in display_lines]
        
        # Position text based on orientation
        if angle == 0:  # Horizontal (top/bottom)
            if len(text_surfaces) == 2:
                # Two lines: center vertically
                y_offset = rect.centery - 10
                text_rect1 = text_surfaces[0].get_rect(center=(rect.centerx, y_offset - 6))
                text_rect2 = text_surfaces[1].get_rect(center=(rect.centerx, y_offset + 6))
                self.screen.blit(text_surfaces[0], text_rect1)
                self.screen.blit(text_surfaces[1], text_rect2)
            else:
                # Single line
                text_rect = text_surfaces[0].get_rect(center=(rect.centerx, rect.centery - 10))
                self.screen.blit(text_surfaces[0], text_rect)
        elif angle == 90:  # Left side
            if len(text_surfaces) == 2:
                y_offset = rect.centery - 8
                text_rect1 = text_surfaces[0].get_rect(center=(rect.centerx, y_offset - 6))
                text_rect2 = text_surfaces[1].get_rect(center=(rect.centerx, y_offset + 6))
                self.screen.blit(text_surfaces[0], text_rect1)
                self.screen.blit(text_surfaces[1], text_rect2)
            else:
                text_rect = text_surfaces[0].get_rect(center=(rect.centerx, rect.centery - 8))
                self.screen.blit(text_surfaces[0], text_rect)
        else:  # Right side (270)
            if len(text_surfaces) == 2:
                y_offset = rect.centery - 8
                text_rect1 = text_surfaces[0].get_rect(center=(rect.centerx, y_offset - 6))
                text_rect2 = text_surfaces[1].get_rect(center=(rect.centerx, y_offset + 6))
                self.screen.blit(text_surfaces[0], text_rect1)
                self.screen.blit(text_surfaces[1], text_rect2)
            else:
                text_rect = text_surfaces[0].get_rect(center=(rect.centerx, rect.centery - 8))
                self.screen.blit(text_surfaces[0], text_rect)
    
    def _draw_property_info(self, rect, pos_idx, info):
        """Draw property value and ownership indicator"""
        space_name = BOARD_LAYOUT[pos_idx]
        
        # Draw price at bottom of space
        if info.get('value', 0) > 0:
            price_text = self.font_tiny.render(f"${info['value']}", True, (0, 0, 0))
            price_rect = price_text.get_rect(bottomright=(rect.right - 4, rect.bottom - 4))
            self.screen.blit(price_text, price_rect)
        
        # Find property by position index to check ownership
        if pos_idx >= len(properties):
            return
        
        # Find property object by matching name
        prop = None
        for p in properties:
            if p.name == space_name:
                prop = p
                break
        
        # Draw ownership indicator (colored bar at top)
        if prop is not None and prop.owner is not None:
            owner_color = COLOR_PLAYER_1 if prop.owner == 0 else COLOR_PLAYER_2
            owner_bar_height = 6
            owner_bar = pygame.Rect(rect.left, rect.top, rect.width, owner_bar_height)
            pygame.draw.rect(self.screen, owner_color, owner_bar)
            pygame.draw.rect(self.screen, COLOR_OWNED_BORDER, owner_bar, 2)
    
    def _draw_players(self):
        """Draw player pieces on the board with smooth animation"""
        for player in self.players:
            pos_idx = player.position % 40
            pos_info = self.board_renderer.get_position(pos_idx)
            
            if pos_info is None:
                continue
            
            rect = pos_info['rect']
            player_color = COLOR_PLAYER_1 if player.ID == 0 else COLOR_PLAYER_2
            
            # Calculate piece position with offset for multiple players on same space
            piece_size = 18
            offset = player.ID * 10
            
            # Ensure piece fits in space
            if rect.width < piece_size + offset + 5:
                offset = 2
            if rect.height < piece_size + offset + 5:
                offset = 2
            
            piece_x = rect.left + 5 + offset
            piece_y = rect.top + 5 + offset
            
            # Draw player piece (circle)
            pygame.draw.circle(self.screen, player_color,
                             (piece_x + piece_size//2, piece_y + piece_size//2),
                             piece_size//2)
            pygame.draw.circle(self.screen, COLOR_BORDER,
                             (piece_x + piece_size//2, piece_y + piece_size//2),
                             piece_size//2, 2)
            
            # Draw player number
            player_num_text = self.font_small.render(str(player.ID + 1), True, (255, 255, 255))
            num_rect = player_num_text.get_rect(center=(piece_x + piece_size//2, piece_y + piece_size//2))
            self.screen.blit(player_num_text, num_rect)
    
    def render_ai_panel(self):
        """Render the AI insights panel"""
        panel_x = self.board_width + 15
        panel_y = 0
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, self.window_height)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, panel_rect, 3)
        
        y_offset = 15
        
        # Title with background
        title_bg = pygame.Rect(panel_x + 10, y_offset, self.panel_width - 20, 35)
        pygame.draw.rect(self.screen, (139, 0, 0), title_bg)
        title = self.font_large.render("AI INSIGHTS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(panel_x + self.panel_width//2, y_offset + 17))
        self.screen.blit(title, title_rect)
        y_offset += 50
        
        # Player 1 stats (FIXED POSITION)
        self._draw_player_stats(panel_x, y_offset, self.players[0], COLOR_PLAYER_1, 0)
        y_offset += 130
        
        # Player 2 stats (FIXED POSITION)
        self._draw_player_stats(panel_x, y_offset, self.players[1], COLOR_PLAYER_2, 1)
        y_offset += 145
        
        # Control buttons
        self._draw_control_buttons(panel_x, y_offset)
        y_offset += 80
        
        # Game log with scroll
        log_bg = pygame.Rect(panel_x + 10, y_offset, self.panel_width - 20, 30)
        pygame.draw.rect(self.screen, (70, 130, 180), log_bg)
        log_title = self.font_medium.render("Game Log (↑↓ or scroll)", True, (255, 255, 255))
        log_title_rect = log_title.get_rect(center=(panel_x + self.panel_width//2, y_offset + 15))
        self.screen.blit(log_title, log_title_rect)
        y_offset += 40
        
        self._draw_game_log(panel_x, y_offset)
    
    def _draw_control_buttons(self, panel_x, y_offset):
        """Draw start/pause/reset buttons and speed slider"""
        # Button dimensions
        button_width = 60
        button_height = 30
        margin = 8
        
        start_x = panel_x + 15
        
        # START button
        self.start_button_rect = pygame.Rect(start_x, y_offset, button_width, button_height)
        
        if not self.game_running:
            pygame.draw.rect(self.screen, (34, 139, 34), self.start_button_rect)  # Green
            start_text = self.font_small.render("START", True, (255, 255, 255))
        else:
            pygame.draw.rect(self.screen, (128, 128, 128), self.start_button_rect)  # Gray
            start_text = self.font_small.render("Run", True, (200, 200, 200))
        
        pygame.draw.rect(self.screen, COLOR_BORDER, self.start_button_rect, 2)
        text_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, text_rect)
        
        # PAUSE/RESUME button
        pause_x = start_x + button_width + margin
        self.pause_button_rect = pygame.Rect(pause_x, y_offset, button_width, button_height)
        
        if self.game_running:
            if self.paused:
                pygame.draw.rect(self.screen, (0, 128, 255), self.pause_button_rect)  # Blue
                pause_text = self.font_tiny.render("RESUME", True, (255, 255, 255))
            else:
                pygame.draw.rect(self.screen, (255, 140, 0), self.pause_button_rect)  # Orange
                pause_text = self.font_tiny.render("PAUSE", True, (255, 255, 255))
        else:
            pygame.draw.rect(self.screen, (200, 200, 200), self.pause_button_rect)  # Light gray
            pause_text = self.font_tiny.render("PAUSE", True, (150, 150, 150))
        
        pygame.draw.rect(self.screen, COLOR_BORDER, self.pause_button_rect, 2)
        text_rect = pause_text.get_rect(center=self.pause_button_rect.center)
        self.screen.blit(pause_text, text_rect)
        
        # RESET button
        reset_x = pause_x + button_width + margin
        self.reset_button_rect = pygame.Rect(reset_x, y_offset, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 20, 20), self.reset_button_rect)  # Red
        reset_text = self.font_small.render("RESET", True, (255, 255, 255))
        pygame.draw.rect(self.screen, COLOR_BORDER, self.reset_button_rect, 2)
        text_rect = reset_text.get_rect(center=self.reset_button_rect.center)
        self.screen.blit(reset_text, text_rect)
        
        # Speed slider
        slider_y = y_offset + button_height + 15
        slider_label = self.font_small.render(f"Speed: {self.game_speed:.1f}s", True, COLOR_LOG_TEXT)
        self.screen.blit(slider_label, (panel_x + 15, slider_y))
        
        slider_y += 20
        slider_width = self.panel_width - 40
        slider_height = 8
        self.speed_slider_rect = pygame.Rect(panel_x + 20, slider_y, slider_width, slider_height)
        
        # Slider track
        pygame.draw.rect(self.screen, (180, 180, 180), self.speed_slider_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.speed_slider_rect, 1)
        
        # Slider handle
        handle_x = self.speed_slider_rect.left + int(((self.game_speed - 0.2) / 2.8) * slider_width)
        handle_x = max(self.speed_slider_rect.left, min(handle_x, self.speed_slider_rect.right - 12))
        self.speed_slider_handle = pygame.Rect(handle_x, slider_y - 6, 12, 20)
        pygame.draw.rect(self.screen, (70, 130, 180), self.speed_slider_handle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.speed_slider_handle, 2)
    
    def _draw_player_stats(self, panel_x, y_offset, player, player_color, player_idx):
        """Draw player statistics in the AI panel"""
        # Player card background
        card_bg = pygame.Rect(panel_x + 10, y_offset, self.panel_width - 20, 125)
        pygame.draw.rect(self.screen, (255, 255, 255), card_bg)
        pygame.draw.rect(self.screen, player_color, card_bg, 3)
        
        # Player header with color indicator - show 1-indexed player number
        player_name = f"🤖 Player {player.ID + 1}"
        header_text = self.font_medium.render(player_name, True, player_color)
        self.screen.blit(header_text, (panel_x + 20, y_offset + 8))
        
        y_offset += 35
        
        # Balance with icon
        balance_text = self.font_small.render(f"💰 Balance: ${player.balance}", True, COLOR_LOG_TEXT)
        self.screen.blit(balance_text, (panel_x + 20, y_offset))
        y_offset += 22
        
        # Properties with icon
        prop_count_text = self.font_small.render(f"🏠 Properties: {len(player.properties)}", True, COLOR_LOG_TEXT)
        self.screen.blit(prop_count_text, (panel_x + 20, y_offset))
        y_offset += 22
        
        # Position with full name
        pos_idx = player.position % 40
        pos_name = BOARD_LAYOUT[pos_idx]
        pos_text = self.font_small.render(f"📍 At: {pos_name[:20]}", True, COLOR_LOG_TEXT)
        self.screen.blit(pos_text, (panel_x + 20, y_offset))
        y_offset += 22
        
        # Bankruptcy risk with visual indicator
        if player.balance < 200:
            risk_color = (200, 0, 0) if player.balance < 0 else (255, 140, 0)
            risk_text = self.font_small.render(f"⚠️ Risk: CRITICAL", True, risk_color)
            self.screen.blit(risk_text, (panel_x + 20, y_offset))
        else:
            risk_text = self.font_small.render(f"✓ Risk: SAFE", True, (0, 150, 0))
            self.screen.blit(risk_text, (panel_x + 20, y_offset))
    
    def _wrap_text(self, text, max_width=42):
        """Wrap text to fit within max_width characters"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text[:max_width]]
    
    def _draw_game_log(self, panel_x, y_offset):
        """Draw recent game events log with scrolling and text wrapping"""
        # Log background
        log_bg_rect = pygame.Rect(panel_x + 10, y_offset, self.panel_width - 30, 
                                 self.window_height - y_offset - 10)
        pygame.draw.rect(self.screen, COLOR_LOG_BG, log_bg_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), log_bg_rect, 2)
        
        # Expand log lines by wrapping long text
        expanded_lines = []
        for line in self.game_log:
            wrapped = self._wrap_text(line, max_width=42)
            expanded_lines.extend(wrapped)
        
        # Calculate visible lines
        available_height = self.window_height - y_offset - 20
        line_height = 16
        max_visible_lines = available_height // line_height
        
        # Adjust scroll offset - allow scrolling to show last line at bottom
        max_scroll = max(0, len(expanded_lines) - max_visible_lines)
        self.log_scroll_offset = max(0, min(self.log_scroll_offset, max_scroll))
        
        # Get visible log lines
        start_idx = self.log_scroll_offset
        end_idx = min(start_idx + max_visible_lines, len(expanded_lines))
        log_lines = expanded_lines[start_idx:end_idx]
        
        y_pos = y_offset + 6
        for i, line in enumerate(log_lines):
            # Alternate background for readability
            if i % 2 == 0:
                line_bg = pygame.Rect(panel_x + 12, y_pos - 2, self.panel_width - 34, line_height)
                pygame.draw.rect(self.screen, (248, 248, 248), line_bg)
            
            log_text = self.font_tiny.render(line, True, COLOR_LOG_TEXT)
            self.screen.blit(log_text, (panel_x + 16, y_pos))
            y_pos += line_height
        
        # Draw scrollbar if needed
        if len(expanded_lines) > max_visible_lines:
            scrollbar_x = panel_x + self.panel_width - 25
            scrollbar_height = log_bg_rect.height - 4
            scrollbar_rect = pygame.Rect(scrollbar_x, y_offset + 2, 12, scrollbar_height)
            pygame.draw.rect(self.screen, (220, 220, 220), scrollbar_rect)
            
            # Scrollbar handle
            handle_ratio = max_visible_lines / len(expanded_lines)
            handle_height = max(20, int(scrollbar_height * handle_ratio))
            handle_y_ratio = self.log_scroll_offset / max(1, max_scroll) if max_scroll > 0 else 0
            handle_y = y_offset + 2 + int((scrollbar_height - handle_height) * handle_y_ratio)
            
            handle_rect = pygame.Rect(scrollbar_x, handle_y, 12, handle_height)
            pygame.draw.rect(self.screen, (100, 100, 100), handle_rect)
            pygame.draw.rect(self.screen, (70, 70, 70), handle_rect, 1)
    
    def add_game_log(self, message):
        """Add a message to the game log"""
        self.game_log.append(message)
        if len(self.game_log) > self.max_log_lines:
            self.game_log.pop(0)
    
    def render(self):
        """Render entire UI"""
        self.render_board()
        self.render_ai_panel()
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_UP:
                    self.log_scroll_offset = max(0, self.log_scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    self.log_scroll_offset += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
                elif event.button == 4:  # Scroll up
                    self.log_scroll_offset = max(0, self.log_scroll_offset - 3)
                elif event.button == 5:  # Scroll down
                    self.log_scroll_offset += 3
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_slider:
                    self._handle_slider_drag(event.pos)
        return True
    
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks on buttons"""
        if self.start_button_rect and self.start_button_rect.collidepoint(pos):
            if not self.game_running:
                self.start_game()
        elif self.pause_button_rect and self.pause_button_rect.collidepoint(pos):
            if self.game_running:
                self.paused = not self.paused
        elif self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.reset_game()
        elif self.speed_slider_handle and self.speed_slider_handle.collidepoint(pos):
            self.dragging_slider = True
    
    def _handle_slider_drag(self, pos):
        """Handle dragging the speed slider"""
        if self.speed_slider_rect:
            x = max(self.speed_slider_rect.left, min(pos[0], self.speed_slider_rect.right))
            relative_x = (x - self.speed_slider_rect.left) / self.speed_slider_rect.width
            self.game_speed = 0.2 + (relative_x * 2.8)  # 0.2 to 3.0 seconds
    
    def start_game(self):
        """Start the AI game in a separate thread"""
        if not self.game_running:
            self.game_running = True
            self.game_log = []  # Clear log
            self.log_scroll_offset = 0
            self.add_game_log("=" * 30)
            self.add_game_log("🎮 AI MONOPOLY GAME STARTED")
            self.add_game_log("=" * 30)
            
            # Initialize game state
            self.players[0].position = 0
            self.players[1].position = 0
            self.last_balances = {0: 1500, 1: 1500}
            self.last_utility_scores = {0: 0, 1: 0}
            self.current_node = Node(properties, self.players[0], self.players[1], "non-chance", None)
            
            # Start game thread
            self.game_thread = threading.Thread(target=self._run_game_loop, daemon=True)
            self.game_thread.start()
    
    def _run_game_loop(self):
        """Main game loop running in separate thread"""
        try:
            mono_tree = tree.MonopolyTree(self.current_node)
            intelligence_level = 3
            mono_tree.generate_tree(intelligence_level)
            Node.Eval(mono_tree)
            
            move_count = 0
            max_moves = 1000
            
            while move_count < max_moves and self.game_running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Check win conditions
                with self.update_lock:
                    if self.current_node.current_player.balance > 2000 or self.current_node.second_player.balance < 0:
                        player_id = self.current_node.current_player.ID
                        self.add_game_log("=" * 30)
                        self.add_game_log(f"🏆 PLAYER {player_id + 1} WINS! 🏆")
                        self.add_game_log("=" * 30)
                        break
                    elif self.current_node.current_player.balance < 0 or self.current_node.second_player.balance > 2000:
                        player_id = self.current_node.second_player.ID
                        self.add_game_log("=" * 30)
                        self.add_game_log(f"🏆 PLAYER {player_id + 1} WINS! 🏆")
                        self.add_game_log("=" * 30)
                        break
                
                # Generate tree if needed
                if len(self.current_node.action) == 0:
                    mono_tree = tree.MonopolyTree(self.current_node)
                    mono_tree.generate_tree(intelligence_level)
                    Node.Eval(mono_tree)
                
                # Process turn
                if self.current_node.node_type == "chance":
                    # Dice roll
                    dice = random.randint(1, 6)
                    player_id = self.current_node.current_player.ID
                    self.add_game_log(f"🎲 P{player_id + 1} rolled {dice}")
                    
                    with self.update_lock:
                        self.current_node = self.current_node.action[dice - 1][1]
                    
                else:
                    # AI decision
                    with self.update_lock:
                        if self.current_node.current_player.ID == 0:
                            self.current_node.action.sort(key=lambda x: x[1].zero_value, reverse=True)
                        else:
                            self.current_node.action.sort(key=lambda x: x[1].one_value, reverse=True)
                        
                        best_action = self.current_node.action[0]
                        action_name = best_action[0]
                        player_id = self.current_node.current_player.ID
                        old_balance = self.current_node.current_player.balance
                        pos_idx = self.current_node.current_player.position % 40
                        pos_name = BOARD_LAYOUT[pos_idx]
                        
                        # Get utility scores before move
                        old_utility = self.current_node.zero_value if player_id == 0 else self.current_node.one_value
                        
                        self.current_node = best_action[1]
                        
                        # Calculate changes
                        new_balance = self.current_node.current_player.balance
                        balance_change = new_balance - old_balance
                        new_utility = self.current_node.zero_value if player_id == 0 else self.current_node.one_value
                        
                        # Store utility scores
                        self.last_utility_scores[player_id] = new_utility
                        
                        # Format action name
                        action_display = action_name.replace('_', ' ').title()
                        
                        # Log with balance change and current balance
                        if balance_change != 0:
                            change_str = f"+${balance_change}" if balance_change > 0 else f"-${abs(balance_change)}"
                            self.add_game_log(f"P{player_id + 1} @ {pos_name[:10]}: {action_display} ({change_str}, now: ${new_balance})")
                        else:
                            self.add_game_log(f"P{player_id + 1} @ {pos_name[:10]}: {action_display}")
                        
                        # Debug: utility score
                        self.add_game_log(f"  └─ Utility: {new_utility:.0f} (Δ{new_utility - old_utility:.0f})")
                
                # Update player object references while preserving fixed ordering by ID
                with self.update_lock:
                    # Map players by ID from the node so UI ordering is stable
                    node_p0 = None
                    node_p1 = None
                    try:
                        # current_node.current_player and second_player are Player objects
                        candidates = [self.current_node.current_player, self.current_node.second_player]
                        for p in candidates:
                            if p.ID == 0:
                                node_p0 = p
                            elif p.ID == 1:
                                node_p1 = p
                    except Exception:
                        # Fallback: assign as-is
                        node_p0 = self.current_node.current_player if hasattr(self.current_node.current_player, 'ID') and self.current_node.current_player.ID == 0 else self.players[0]
                        node_p1 = self.current_node.second_player if hasattr(self.current_node.second_player, 'ID') and self.current_node.second_player.ID == 1 else self.players[1]

                    # Ensure we always keep players[0] = ID 0 and players[1] = ID 1
                    if node_p0 is not None:
                        self.players[0] = node_p0
                    if node_p1 is not None:
                        self.players[1] = node_p1

                    # Update last known balances
                    self.last_balances[0] = self.players[0].balance
                    self.last_balances[1] = self.players[1].balance
                
                move_count += 1
                time.sleep(self.game_speed)
            
            if move_count >= max_moves:
                self.add_game_log("⏱️ Max moves reached")
            
        except Exception as e:
            import traceback
            self.add_game_log(f"❌ Error: {str(e)[:50]}")
            print(f"Game error: {e}")
            traceback.print_exc()
        finally:
            self.game_running = False
    
    def reset_game(self):
        """Reset the game"""
        self.game_running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        
        # Reinitialize players with fresh state
        self.players = [Player(0, balance=1500, position=0), Player(1, balance=1500, position=0)]
        for player in self.players:
            player.in_jail = False
            player.jail_turns = 0
            if hasattr(player, 'get_out_of_jail_free_cards'):
                player.get_out_of_jail_free_cards = 0
        
        # Reset all properties
        for prop in properties:
            prop.owner = None
        
        # Create fresh game node
        self.current_node = Node(properties, self.players[0], self.players[1], "non-chance", None)
        self.game_log = []
        self.log_scroll_offset = 0
        
        # Initialize balance tracking
        self.last_balances = {0: self.players[0].balance, 1: self.players[1].balance}
        self.last_utility_scores = {0: 0.0, 1: 0.0}
        
        self.add_game_log("🔄 Game reset")
        self.add_game_log("Press START to begin")
    
    def run(self):
        """Main game loop"""
        running = True
        self.start_game()
        
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(self.fps)
        
        self.game_running = False
        pygame.quit()
        sys.exit()


def main():
    """Main entry point"""
    game = GameUI()
    game.run()


if __name__ == "__main__":
    main()
