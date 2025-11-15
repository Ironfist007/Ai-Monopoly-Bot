import tkinter as tk
from tkinter import ttk
import random
import threading
import time
from property import properties
from player import Player
from game import Game
from node import Node
import tree
import copy

class AIMonopolyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Monopoly Game - Watch AI Players Battle!")
        # Start with a sensible default; we will auto-resize below
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f8ff')
        
        # Game state - players start at GO (visual board position 0)
        self.players = [Player(0, position=0), Player(1, position=0)]  # Start both players at GO
        self.game = Game(self.players)
        self.current_node = None
        self.game_running = False
        self.game_speed = 2.0  # seconds between moves
        
        # Board configuration (responsive to window size)
        # We'll compute an initial size based on the screen height.
        self.control_panel_width = 420
        self.outer_margin = 40  # combined padding/margins
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # Keep the board within the visible screen area accounting for margins and controls
        initial_board = min(
            max(600, int(screen_h * 0.75)),  # prefer 75% of screen height
            max(600, int(screen_w * 0.75))   # but also keep reasonable wrt width
        )
        self.board_size = int(initial_board)
        # Corner and strip thickness proportional to the board size
        self.corner_size = max(90, int(self.board_size * 0.12))
        available_space = self.board_size - (2 * self.corner_size)
        self.property_size = available_space / 9
        self.side_property_height = max(70, int(self.board_size * 0.10))
        
        # Monopoly board layout (40 spaces)
        self.board_layout = [
            # Bottom row (0-10)
            "GO", "Mediterranean Avenue", "Community Chest", "Baltic Avenue", "Income Tax",
            "Reading Railroad", "Oriental Avenue", "Chance", "Vermont Avenue", "Connecticut Avenue", "JAIL",
            # Left side (11-20)  
            "St. Charles Place", "Electric Company", "States Avenue", "Virginia Avenue",
            "Pennsylvania Railroad", "St. James Place", "Community Chest", "Tennessee Avenue", "New York Avenue", "FREE PARKING",
            # Top row (21-30)
            "Kentucky Avenue", "Chance", "Indiana Avenue", "Illinois Avenue", "B&O Railroad",
            "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens", "GO TO JAIL",
            # Right side (31-39)
            "Pacific Avenue", "North Carolina Avenue", "Community Chest", "Pennsylvania Avenue", "Short Line Railroad",
            "Chance", "Park Place", "Luxury Tax", "Boardwalk"
        ]
        
        # Colors for different property types
        self.property_colors = {
            'Mediterranean Avenue': '#8B4513', 'Baltic Avenue': '#8B4513',  # Brown
            'Oriental Avenue': '#87CEEB', 'Vermont Avenue': '#87CEEB', 'Connecticut Avenue': '#87CEEB',  # Light Blue
            'St. Charles Place': '#FF69B4', 'States Avenue': '#FF69B4', 'Virginia Avenue': '#FF69B4',  # Pink
            'St. James Place': '#FFA500', 'Tennessee Avenue': '#FFA500', 'New York Avenue': '#FFA500',  # Orange
            'Kentucky Avenue': '#FF0000', 'Indiana Avenue': '#FF0000', 'Illinois Avenue': '#FF0000',  # Red
            'Atlantic Avenue': '#FFFF00', 'Ventnor Avenue': '#FFFF00', 'Marvin Gardens': '#FFFF00',  # Yellow
            'Pacific Avenue': '#00FF00', 'North Carolina Avenue': '#00FF00', 'Pennsylvania Avenue': '#00FF00',  # Green
            'Park Place': '#000080', 'Boardwalk': '#000080',  # Dark Blue
            'Reading Railroad': '#D90166', 'Pennsylvania Railroad': '#D90166', 'B&O Railroad': '#D90166', 'Short Line Railroad': '#D90166',  # Railroads
            'Electric Company': '#FFFFFF', 'Water Works': '#FFFFFF',  # Utilities
        }
        
        # Build mapping from properties (from property.py) to visual board indices
        # property.py defines a list of Property objects (usually 30). The visual board
        # has 40 spaces. We'll map each property (by name, in order) to the next matching
        # board index in `self.board_layout`. For duplicate names like "Community Chest"
        # we consume occurrences in order so each Property maps to a distinct visual slot.
        name_to_indices = {}
        for idx, name in enumerate(self.board_layout):
            name_to_indices.setdefault(name, []).append(idx)

        # prop_index -> visual board index
        self.prop_to_board_index = []
        for prop in properties:
            lst = name_to_indices.get(prop.name, [])
            if lst:
                board_idx = lst.pop(0)
            else:
                # If name not found (or we've exhausted duplicates), try fuzzy match
                board_idx = None
                for k, v in name_to_indices.items():
                    if prop.name in k or k in prop.name:
                        if v:
                            board_idx = v.pop(0)
                            break
                # Fallback: place sequentially after last assigned index
                if board_idx is None:
                    board_idx = len(self.prop_to_board_index) % 40
            self.prop_to_board_index.append(board_idx)

        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Board canvas (sized to current board size)
        self.canvas = tk.Canvas(main_frame, width=self.board_size, height=self.board_size,
                       bg='#e6ffe6', highlightthickness=2, highlightbackground='#000000')
        self.canvas.pack(side='left', padx=(0, 20))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#f0f8ff', width=420)
        control_frame.pack(side='right', fill='y')
        control_frame.pack_propagate(False)
        
        self.setup_control_panel(control_frame)
        
        # Make the board responsive to window resizing so the bottom row always fits
        self.root.bind('<Configure>', self.on_window_resize)
        self.draw_board()
        self.draw_players()
        
    def setup_control_panel(self, parent):
        # Title
        title_label = tk.Label(parent, text="AI MONOPOLY", font=('Arial', 20, 'bold'), 
                              fg='#8B0000', bg='#f0f8ff')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(parent, text="Watch AI Players Battle!", font=('Arial', 12), 
                                 fg='#4B0000', bg='#f0f8ff')
        subtitle_label.pack()
        
        # Player info
        self.player_info_frame = tk.Frame(parent, bg='#f0f8ff')
        self.player_info_frame.pack(fill='x', pady=10)
        
        # AI Controls
        ai_frame = tk.Frame(parent, bg='#f0f8ff')
        ai_frame.pack(pady=10)
        
        tk.Label(ai_frame, text="AI Controls", font=('Arial', 14, 'bold'), bg='#f0f8ff').pack()
        
        # Speed control
        speed_frame = tk.Frame(ai_frame, bg='#f0f8ff')
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Game Speed:", bg='#f0f8ff').pack(side='left')
        self.speed_var = tk.DoubleVar(value=2.0)
        speed_scale = tk.Scale(speed_frame, from_=0.5, to=5.0, resolution=0.5, 
                              orient='horizontal', variable=self.speed_var,
                              command=self.update_speed, bg='#f0f8ff')
        speed_scale.pack(side='left')
        
        # Control buttons
        self.start_button = tk.Button(ai_frame, text="Start AI Game", font=('Arial', 12, 'bold'),
                                     bg='#4CAF50', fg='white', command=self.start_ai_game)
        self.start_button.pack(pady=5)
        
        self.pause_button = tk.Button(ai_frame, text="Pause", font=('Arial', 12),
                                     bg='#FF9800', fg='white', command=self.pause_game, state='disabled')
        self.pause_button.pack(pady=2)
        
        self.reset_button = tk.Button(ai_frame, text="Reset Game", font=('Arial', 12),
                                     bg='#f44336', fg='white', command=self.reset_game)
        self.reset_button.pack(pady=2)
        
        # Current dice display
        dice_frame = tk.Frame(parent, bg='#f0f8ff')
        dice_frame.pack(pady=10)
        
        tk.Label(dice_frame, text="Current Dice Roll", font=('Arial', 12, 'bold'), bg='#f0f8ff').pack()
        # Larger dice display for clarity
        self.dice_canvas = tk.Canvas(dice_frame, width=100, height=100, bg='white')
        self.dice_canvas.pack(pady=5)
        self.current_dice = 1
        
        # Game info
        tk.Label(parent, text="Game Log", font=('Arial', 12, 'bold'), bg='#f0f8ff').pack()
        self.info_text = tk.Text(parent, height=20, width=40, font=('Arial', 9))
        self.info_text.pack(pady=5, fill='both', expand=True)
        
        # Scrollbar for text
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side='right', fill='y')
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
        self.update_player_info()
        self.draw_dice()
        
    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw board background
        self.canvas.create_rectangle(0, 0, self.board_size, self.board_size, 
                                   fill='#e6ffe6', outline='black', width=2)
        
        # Draw center area with proper proportions
        center_margin = int(self.board_size * 0.22)  # Balanced center area
        self.canvas.create_rectangle(center_margin, center_margin, 
                                   self.board_size - center_margin, 
                                   self.board_size - center_margin,
                                   fill='#f0f8ff', outline='black', width=2)
        
        # Draw MONOPOLY logo in center with proper sizing
        self.canvas.create_text(self.board_size//2, self.board_size//2 - 35, 
                      text="MONOPOLY", font=('Arial', 32, 'bold'), 
                      fill='#8B0000')
        
        self.canvas.create_text(self.board_size//2, self.board_size//2 + 15, 
                      text="AI BATTLE", font=('Arial', 20, 'bold'), 
                      fill='#4B0000')
        
        # Draw properties around the board
        self.draw_properties()
        
    def draw_properties(self):
        board_positions = self.get_board_layout()
        
        corners = {0: "GO", 10: "JAIL", 20: "FREE PARKING", 30: "GO TO JAIL"}
        
        # First pass: draw all non-corner cells (ensures corners cap the edges visually)
        for i, pos_info in enumerate(board_positions):
            if i in corners:
                continue
            x, y, width, height = pos_info['rect']
            
            # Get property name
            prop_name = self.board_layout[i] if i < len(self.board_layout) else f"Space {i}"
            
            # Get property color
            color = '#f0f0f0'  # Default color
            if prop_name in self.property_colors:
                color = self.property_colors[prop_name]
            elif i in [0, 10, 20, 30]:  # Corner spaces
                color = '#ffcccb'
            elif 'Community Chest' in prop_name or 'Chance' in prop_name:
                color = '#ffd700'
            elif 'Tax' in prop_name:
                color = '#ff6b6b'
            
            # Draw property rectangle
            self.canvas.create_rectangle(x, y, x + width, y + height, 
                                       fill=color, outline='black', width=1)
            
            # Draw property name with tighter truncation and smaller fonts to avoid overflow
            name = prop_name
            angle = pos_info['text_angle']

            # Smart text handling based on orientation and space
            if angle in [0, 180]:  # Horizontal properties (top/bottom)
                if len(name) > 9:
                    words = name.split()
                    if len(words) > 1:
                        name = words[0][:6] + "\n" + " ".join(words[1:])[:6]
                    else:
                        name = name[:7]
                text_x = x + width // 2
                text_y = y + height // 2 - int(height * 0.18)
                font_size = 7
            elif angle == 90:  # Left side (vertical) - position name higher to make room for price below
                if len(name) > 12:
                    words = name.split()
                    if len(words) > 1:
                        name = words[0][:8] + "\n" + " ".join(words[1:])[:8]
                    else:
                        name = name[:10]
                text_x = x + width // 2 + 5
                text_y = y + height // 2 - int(height * 0.15)  # Move name up to leave room for price
                font_size = 6
            else:  # angle == 270, Right side (vertical) - position name higher to make room for price below
                if len(name) > 12:
                    words = name.split()
                    if len(words) > 1:
                        name = words[0][:8] + "\n" + " ".join(words[1:])[:8]
                    else:
                        name = name[:10]
                text_x = x + width // 2 - 5
                text_y = y + height // 2 - int(height * 0.15)  # Move name up to leave room for price
                font_size = 6

            self.canvas.create_text(
                text_x, text_y, text=name,
                font=('Arial', font_size, 'bold'),
                angle=angle,
                justify='center',
                width=max(8, width - 4),  # constrain width so it wraps instead of overflowing
                fill='black'
            )
            
            # (Prices and ownership are drawn after the board loop using the
            # mapping between properties and visual positions so that properties
            # defined in property.py can be placed on any visual index.)

        # Draw corner cells last so they sit above edge strips
        for i, label in corners.items():
            pos_info = board_positions[i]
            x, y, width, height = pos_info['rect']
            self.canvas.create_rectangle(x, y, x + width, y + height,
                                         fill='#ffcccb', outline='black', width=1)
            # Corner labels
            self.canvas.create_text(x + width//2, y + height//2,
                                    text=label, font=('Arial', 10, 'bold'))

        # Draw prices and ownership indicators using the mapping from
        # property list index -> visual board index
        for p_idx, prop in enumerate(properties):
            if p_idx >= len(self.prop_to_board_index):
                continue
            board_idx = self.prop_to_board_index[p_idx]
            if board_idx is None or board_idx >= len(board_positions):
                continue
            pos = board_positions[board_idx]
            x, y, w, h = pos['rect']
            text_x = x + w // 2
            text_y = y + h // 2
            angle = pos['text_angle']

            # Price placement for clear separation from name - adjusted for vertical properties
            if angle == 0:  # Horizontal (bottom row) - price below name
                price_y = y + (h * 0.75)
                price_x = text_x
            elif angle == 90:  # Left side (vertical) - price to the right of name
                price_y = y + (h * 0.5)
                price_x = x + (w * 0.75)  # Position price to the right
            elif angle == 270:  # Right side (vertical) - price to the left of name
                price_y = y + (h * 0.5)
                price_x = x + (w * 0.25)  # Position price to the left
            else:  # Horizontal (top row) - price above name
                price_y = y + (h * 0.25)
                price_x = text_x

            price_text = f"${prop.value}"
            # Reduce price font to prevent overflow in small boxes
            price_font_size = 6
            self.canvas.create_text(price_x, price_y, text=price_text,
                                  font=('Arial', price_font_size, 'bold'), fill='#006400',
                                  angle=angle)

            # Ownership indicator - larger and more visible
            if getattr(prop, 'owner', None) is not None:
                owner_color = 'red' if prop.owner == 0 else 'blue'
                owner_size = max(12, int(min(w, h) * 0.2))
                # Position in corner for visibility
                owner_x = x + w - owner_size - 3
                owner_y = y + 3
                self.canvas.create_rectangle(owner_x, owner_y, owner_x + owner_size, owner_y + owner_size,
                                            fill=owner_color, outline='white', width=2, tags='owner')

        # Redraw bottom row (indices 1..9) on top to guarantee visibility (corners already redrawn)
        for i in range(1, 10):
            pos_info = board_positions[i]
            x, y, width, height = pos_info['rect']
            prop_name = self.board_layout[i] if i < len(self.board_layout) else f"Space {i}"
            # Background color
            color = '#f0f0f0'
            if prop_name in self.property_colors:
                color = self.property_colors[prop_name]
            elif 'Community Chest' in prop_name or 'Chance' in prop_name:
                color = '#ffd700'
            elif 'Tax' in prop_name:
                color = '#ff6b6b'
            # Draw cell
            self.canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline='black', width=1)
            # Name (smaller font for bottom row)
            name = prop_name
            if pos_info['text_angle'] in [0, 180]:
                if len(name) > 9:
                    words = name.split()
                    if len(words) > 1:
                        name = words[0][:6] + "\n" + " ".join(words[1:])[:6]
                    else:
                        name = name[:7]
            text_x = x + width // 2
            text_y = y + height // 2 - int(height * 0.18)
            self.canvas.create_text(text_x, text_y, text=name,
                                    font=('Arial', 8, 'bold'), justify='center', fill='black')
            # Price
            if i < len(properties):
                p_idx = i if i < len(self.prop_to_board_index) else None
                # Use properties by mapping when available, else fallback to same index
                prop = properties[p_idx] if p_idx is not None and p_idx < len(properties) else None
                if prop is None and i < len(properties):
                    prop = properties[i]
                if prop is not None:
                    price_text = f"${prop.value}"
                    price_y = y + (height * 0.72)
                    self.canvas.create_text(text_x, price_y, text=price_text,
                                            font=('Arial', 8, 'bold'), fill='#006400')
    
    def get_board_layout(self):
        """Returns layout information for all 40 board positions"""
        positions = []
        corner = self.corner_size
        prop_size = self.property_size
        thickness = self.side_property_height
        
        # Bottom row (0-10) - GO to JAIL (positions 0-10)
        # Position 0: GO corner (bottom-right)
        positions.append({
            'rect': (self.board_size - corner, self.board_size - corner, corner, corner),
            'text_angle': 0
        })
        
        # Positions 1-9: Properties on bottom (right to left)
        for i in range(1, 10):
            x = self.board_size - corner - (i * prop_size)
            positions.append({
                # subtract a couple of pixels to avoid canvas clipping on bottom edge
                'rect': (int(x), self.board_size - thickness - 2, int(prop_size), thickness),
                'text_angle': 0
            })
        
        # Position 10: JAIL corner (bottom-left)
        positions.append({
            'rect': (0, self.board_size - corner, corner, corner),
            'text_angle': 0
        })
        
        # Left side (11-19) - JAIL to FREE PARKING (bottom to top)
        for i in range(1, 10):
            y = self.board_size - corner - (i * prop_size)
            positions.append({
                'rect': (0, int(y), thickness, int(prop_size)),
                'text_angle': 90
            })
        
        # Position 20: FREE PARKING corner (top-left)
        positions.append({
            'rect': (0, 0, corner, corner),
            'text_angle': 0
        })
        
        # Top row (21-29) - FREE PARKING to GO TO JAIL (left to right)
        for i in range(1, 10):
            x = corner + ((i - 1) * prop_size)
            positions.append({
                'rect': (int(x), 0, int(prop_size), thickness),
                'text_angle': 0
            })
        
        # Position 30: GO TO JAIL corner (top-right)
        positions.append({
            'rect': (self.board_size - corner, 0, corner, corner),
            'text_angle': 0
        })
        
        # Right side (31-39) - GO TO JAIL to GO (top to bottom)
        for i in range(1, 10):
            y = corner + ((i - 1) * prop_size)
            positions.append({
                'rect': (self.board_size - thickness, int(y), thickness, int(prop_size)),
                'text_angle': 270
            })
        
        return positions

    def _recompute_board_metrics(self):
        """Recalculate sizes derived from board size."""
        self.corner_size = max(90, int(self.board_size * 0.12))
        available_space = self.board_size - (2 * self.corner_size)
        self.property_size = available_space / 9
        self.side_property_height = max(70, int(self.board_size * 0.10))

    def on_window_resize(self, event):
        """Adjust board size when the window is resized to ensure it fits."""
        try:
            # Only handle root window size changes
            if event.widget is not self.root:
                return

            # Compute the maximum board that fits within current window
            avail_w = max(400, event.width - self.control_panel_width - self.outer_margin)
            avail_h = max(400, event.height - self.outer_margin)
            new_board = int(max(500, min(avail_w, avail_h)))

            # Avoid constant redraws on tiny fluctuations
            if abs(new_board - self.board_size) < 8:
                return

            self.board_size = new_board
            self._recompute_board_metrics()
            # Resize canvas and redraw
            self.canvas.config(width=self.board_size, height=self.board_size)
            self.draw_board()
            self.draw_players()
        except Exception:
            # Fail silently on resize race conditions
            pass
    
    def draw_players(self):
        """Draw player pieces on the board"""
        self.canvas.delete("player")
        
        board_positions = self.get_board_layout()

        for i, player in enumerate(self.players):
            # Player.position should directly correspond to visual board positions (0-39)
            # Position 0 = GO, Position 10 = JAIL, etc.
            visual_idx = player.position % len(board_positions)

            if visual_idx >= len(board_positions):
                continue

            pos_info = board_positions[visual_idx]
            x, y, width, height = pos_info['rect']
            # Player colors
            colors = ['red', 'blue', 'green', 'yellow']  # Support more players
            color = colors[i % len(colors)]

            # Player piece size scales with property space
            piece_size = max(12, int(min(width, height) * 0.28))

            # Calculate player position (offset for multiple players on same space)
            offset_x = 6 + (i * (piece_size + 2))
            offset_y = 6 + (i * (piece_size + 2))

            # Ensure the player piece fits within the property space
            if offset_x + piece_size > width:
                offset_x = max(2, width - piece_size - 2)
            if offset_y + piece_size > height:
                offset_y = max(2, height - piece_size - 2)

            # Draw player piece (circle)
            self.canvas.create_oval(x + offset_x, y + offset_y, 
                                  x + offset_x + piece_size, y + offset_y + piece_size,
                                  fill=color, outline='black', 
                                  tags="player", width=2)

            # Add player number inside the piece
            self.canvas.create_text(x + offset_x + piece_size//2, y + offset_y + piece_size//2,
                                  text=str(i + 1), font=('Arial', max(8, int(piece_size*0.4)), 'bold'),
                                  fill='white', tags="player")
    
    def draw_dice(self):
        """Draw current dice value"""
        self.dice_canvas.delete("all")
        
        dice_size = 80  # Larger dice for better visibility
        x, y = 10, 10
        
        # Draw dice background with shadow effect
        self.dice_canvas.create_rectangle(x+2, y+2, x + dice_size+2, y + dice_size+2,
                                        fill='gray', outline='gray')
        self.dice_canvas.create_rectangle(x, y, x + dice_size, y + dice_size,
                                        fill='white', outline='black', width=3)
        
        # Draw dots based on value
        self.draw_dice_dots(x, y, dice_size, self.current_dice)
    
    def draw_dice_dots(self, x, y, size, value):
        """Draw dots on the die"""
        dot_size = 8  # Larger dots for visibility
        center_x = x + size // 2
        center_y = y + size // 2
        spacing = size // 4  # Spacing scaled to dice size
        
        positions = {
            1: [(0, 0)],
            2: [(-spacing, -spacing), (spacing, spacing)],
            3: [(-spacing, -spacing), (0, 0), (spacing, spacing)],
            4: [(-spacing, -spacing), (spacing, -spacing), (-spacing, spacing), (spacing, spacing)],
            5: [(-spacing, -spacing), (spacing, -spacing), (0, 0), (-spacing, spacing), (spacing, spacing)],
            6: [(-spacing, -spacing), (spacing, -spacing), (-spacing, 0), (spacing, 0), (-spacing, spacing), (spacing, spacing)]
        }
        
        for dx, dy in positions[value]:
            self.dice_canvas.create_oval(center_x + dx - dot_size//2, 
                                       center_y + dy - dot_size//2,
                                       center_x + dx + dot_size//2, 
                                       center_y + dy + dot_size//2,
                                       fill='black', outline='gray')
    
    def start_ai_game(self):
        """Start the AI game in a separate thread"""
        if not self.game_running:
            self.game_running = True
            self.start_button.configure(state='disabled')
            self.pause_button.configure(state='normal')
            
            # Initialize AI - make sure players are at GO position
            self.players[0].position = 0  # GO
            self.players[1].position = 0  # GO
            self.current_node = Node(properties, self.players[0], self.players[1], "non-chance", None)
            
            # Start AI game thread
            self.ai_thread = threading.Thread(target=self.run_ai_game, daemon=True)
            self.ai_thread.start()
            
            self.add_game_info("=== AI MONOPOLY GAME STARTED ===")
            self.add_game_info("Watch as AI players make strategic decisions!")
    
    def run_ai_game(self):
        """Main AI game loop"""
        try:
            mono_tree = tree.MonopolyTree(self.current_node)
            intelligence_level = 3  # Reduced for faster gameplay
            mono_tree.generate_tree(intelligence_level)
            Node.Eval(mono_tree)
            
            move_count = 0
            max_moves = 200  # Prevent infinite games
            
            while move_count < max_moves:
                # Handle pause - stay in loop but don't process
                if not self.game_running:
                    time.sleep(0.1)
                    continue
                
                # Check win conditions
                if self.current_node.current_player.balance > 2000 or self.current_node.second_player.balance < 0:
                    self.root.after(0, lambda: self.add_game_info(f"🏆 PLAYER {self.current_node.current_player.ID + 1} WINS! 🏆"))
                    break
                elif self.current_node.current_player.balance < 0 or self.current_node.second_player.balance > 2000:
                    self.root.after(0, lambda: self.add_game_info(f"🏆 PLAYER {self.current_node.second_player.ID + 1} WINS! 🏆"))
                    break
                
                # Generate new tree if needed
                if len(self.current_node.action) == 0:
                    mono_tree = tree.MonopolyTree(self.current_node)
                    mono_tree.generate_tree(intelligence_level)
                    Node.Eval(mono_tree)
                
                # Process turn
                if self.current_node.node_type == "chance":
                    # Dice roll
                    dice = random.randint(1, 6)
                    self.current_dice = dice
                    
                    player_name = f"Player {self.current_node.current_player.ID + 1}"
                    
                    # Check jail status before dice roll
                    if hasattr(self.current_node.current_player, 'in_jail') and self.current_node.current_player.in_jail:
                        self.root.after(0, lambda d=dice, p=player_name: self.add_game_info(f"🎲 {p} (IN JAIL) rolled {d}"))
                    else:
                        self.root.after(0, lambda d=dice, p=player_name: self.add_game_info(f"🎲 {p} rolled {d}"))
                    
                    self.current_node = self.current_node.action[dice - 1][1]
                    
                    # Check if player went to jail
                    if hasattr(self.current_node.current_player, 'in_jail') and self.current_node.current_player.in_jail:
                        self.root.after(0, lambda p=player_name: self.add_game_info(f"🔒 {p} is now in JAIL!"))
                    
                    # Update GUI
                    self.root.after(0, self.update_display)
                    
                else:
                    # AI decision
                    if self.current_node.current_player.ID == 0:
                        self.current_node.action.sort(key=lambda tup: tup[1].zero_value, reverse=True)
                    else:
                        self.current_node.action.sort(key=lambda tup: tup[1].one_value, reverse=True)
                    
                    best_action = self.current_node.action[0]
                    action_name = best_action[0]
                    
                    player_name = f"Player {self.current_node.current_player.ID + 1}"
                    position_name = self.board_layout[self.current_node.current_player.position] if self.current_node.current_player.position < len(self.board_layout) else f"Position {self.current_node.current_player.position}"
                    
                    # Add corner space detection for logging
                    corner_spaces = [0, 10, 20, 30]
                    is_corner = self.current_node.current_player.position in corner_spaces
                    corner_note = " (Corner Space)" if is_corner else ""
                    
                    self.root.after(0, lambda a=action_name, p=player_name, pos=position_name, bal=self.current_node.current_player.balance, note=corner_note: 
                                   self.add_game_info(f"🤖 {p} at {pos}{note} decided to: {a.upper()} (Balance: ${bal})"))
                    
                    self.current_node = best_action[1]
                    
                    # Update GUI
                    self.root.after(0, self.update_display)
                
                move_count += 1
                time.sleep(self.game_speed)
            
            if move_count >= max_moves:
                self.root.after(0, lambda: self.add_game_info("Game ended - Maximum moves reached"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_game_info(f"Error in AI game: {str(e)}"))
        finally:
            self.game_running = False
            self.root.after(0, self.game_ended)
    
    def update_display(self):
        """Update the GUI display"""
        # Update player positions and info
        self.players[0] = self.current_node.current_player
        self.players[1] = self.current_node.second_player
        
        self.draw_players()
        self.draw_dice()
        self.draw_board()  # Redraw to show ownership changes
        self.update_player_info()
    
    def pause_game(self):
        """Pause/Resume the game"""
        if self.game_running:
            self.game_running = False
            self.pause_button.configure(text="Resume")
            self.add_game_info("⏸️ Game Paused")
        else:
            self.game_running = True
            self.pause_button.configure(text="Pause")
            self.add_game_info("▶️ Game Resumed")
    
    def reset_game(self):
        """Reset the game"""
        self.game_running = False
        
        # Reset players with jail attributes
        self.players = [Player(0, position=0), Player(1, position=0)]
        for player in self.players:
            player.in_jail = False
            player.jail_turns = 0
            player.get_out_of_jail_free_cards = 0
        
        # Reset properties
        for prop in properties:
            prop.owner = None
        
        self.current_node = None
        self.current_dice = 1
        
        # Reset UI
        self.start_button.configure(state='normal')
        self.pause_button.configure(state='disabled', text="Pause")
        
        self.draw_board()
        self.draw_players() 
        self.draw_dice()
        self.update_player_info()
        
        self.info_text.delete(1.0, tk.END)
        self.add_game_info("Game Reset - Ready to start new AI battle!")
    
    def game_ended(self):
        """Handle game end"""
        self.start_button.configure(state='normal')
        self.pause_button.configure(state='disabled')
        self.add_game_info("=== GAME OVER ===")
    
    def update_speed(self, value):
        """Update game speed"""
        self.game_speed = float(value)
    
    def update_player_info(self):
        """Update player information display"""
        for widget in self.player_info_frame.winfo_children():
            widget.destroy()
        
        for i, player in enumerate(self.players):
            frame = tk.Frame(self.player_info_frame, bg='lightcoral' if i == 0 else 'lightblue')
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=f"🤖 AI Player {i + 1}", font=('Arial', 12, 'bold'), bg=frame['bg']).pack()
            tk.Label(frame, text=f"💰 Balance: ${player.balance}", bg=frame['bg']).pack()
            tk.Label(frame, text=f"🏠 Properties: {len(player.properties)}", bg=frame['bg']).pack()
            
            # Show jail status
            if hasattr(player, 'in_jail') and player.in_jail:
                tk.Label(frame, text=f"🔒 IN JAIL (Turn {player.jail_turns}/3)", bg='#ffcccc', fg='red', font=('Arial', 10, 'bold')).pack()
            
            # Show current position
            pos_idx = player.position % len(self.board_layout)
            pos_name = self.board_layout[pos_idx] if pos_idx < len(self.board_layout) else f"Position {player.position}"
            tk.Label(frame, text=f"📍 Position: {pos_name}", bg=frame['bg'], wraplength=200).pack()
            
            # Debug: Print player positions
            print(f"DEBUG: AI Player {i+1} at position {player.position} ({pos_name})")
        
        # Redraw players on the board
        self.draw_players()
    
    def add_game_info(self, message):
        """Add message to game info text"""
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """Start the GUI"""
        self.add_game_info("🎮 Welcome to AI Monopoly!")
        self.add_game_info("Click 'Start AI Game' to watch AI players battle!")
        self.add_game_info("Adjust game speed with the slider.")
        self.root.mainloop()

if __name__ == "__main__":
    game_gui = AIMonopolyGUI()
    game_gui.run()