"""
Board configuration with explicit 40-space layout and property mapping.
No fuzzy matching - all positions clearly defined.
"""

# 40 board spaces (0-39) in order: bottom, left, top, right
BOARD_LAYOUT = [
    # Bottom row (0-10): GO to JAIL
    "GO", 
    "Mediterranean Avenue", 
    "Community Chest", 
    "Baltic Avenue", 
    "Income Tax",
    "Reading Railroad", 
    "Oriental Avenue", 
    "Chance", 
    "Vermont Avenue", 
    "Connecticut Avenue", 
    "JAIL",
    
    # Left side (11-20): JAIL to FREE PARKING (going up)
    "St. Charles Place", 
    "Electric Company", 
    "States Avenue", 
    "Virginia Avenue",
    "Pennsylvania Railroad", 
    "St. James Place", 
    "Community Chest", 
    "Tennessee Avenue", 
    "New York Avenue", 
    "FREE PARKING",
    
    # Top row (21-30): FREE PARKING to GO TO JAIL (going right)
    "Kentucky Avenue", 
    "Chance", 
    "Indiana Avenue", 
    "Illinois Avenue", 
    "B&O Railroad",
    "Atlantic Avenue", 
    "Ventnor Avenue", 
    "Water Works", 
    "Marvin Gardens", 
    "GO TO JAIL",
    
    # Right side (31-39): GO TO JAIL to GO (going down)
    "Pacific Avenue", 
    "North Carolina Avenue", 
    "Community Chest", 
    "Pennsylvania Avenue", 
    "Short Line Railroad",
    "Chance", 
    "Park Place", 
    "Luxury Tax", 
    "Boardwalk"
]

# Property colors for visual identification
PROPERTY_COLORS = {
    # Brown
    "Mediterranean Avenue": (139, 69, 35),
    "Baltic Avenue": (139, 69, 35),
    
    # Light Blue
    "Oriental Avenue": (135, 206, 235),
    "Vermont Avenue": (135, 206, 235),
    "Connecticut Avenue": (135, 206, 235),
    
    # Pink/Magenta
    "St. Charles Place": (255, 105, 180),
    "States Avenue": (255, 105, 180),
    "Virginia Avenue": (255, 105, 180),
    
    # Orange
    "St. James Place": (255, 165, 0),
    "Tennessee Avenue": (255, 165, 0),
    "New York Avenue": (255, 165, 0),
    
    # Red
    "Kentucky Avenue": (255, 0, 0),
    "Indiana Avenue": (255, 0, 0),
    "Illinois Avenue": (255, 0, 0),
    
    # Yellow
    "Atlantic Avenue": (255, 255, 0),
    "Ventnor Avenue": (255, 255, 0),
    "Marvin Gardens": (255, 255, 0),
    
    # Green
    "Pacific Avenue": (0, 200, 0),
    "North Carolina Avenue": (0, 200, 0),
    "Pennsylvania Avenue": (0, 200, 0),
    
    # Dark Blue -> Purple (Park Place and Boardwalk)
    "Park Place": (138, 43, 226),
    "Boardwalk": (138, 43, 226),
    
    # Railroads (purple/magenta)
    "Reading Railroad": (217, 1, 102),
    "Pennsylvania Railroad": (217, 1, 102),
    "B&O Railroad": (217, 1, 102),
    "Short Line Railroad": (217, 1, 102),
    
    # Utilities (white)
    "Electric Company": (240, 240, 240),
    "Water Works": (240, 240, 240),
    
    # Corners (special)
    "GO": (230, 230, 230),
    "JAIL": (200, 200, 200),
    "FREE PARKING": (200, 200, 200),
    "GO TO JAIL": (200, 200, 200),
    
    # Special cards
    "Community Chest": (255, 215, 0),
    "Chance": (255, 215, 0),
    
    # Tax
    "Income Tax": (255, 107, 107),
    "Luxury Tax": (255, 107, 107),
}

# Property information: value, is_corner, is_special
PROPERTY_INFO = {
    "GO": {"value": 0, "is_corner": True, "is_special": True},
    "Mediterranean Avenue": {"value": 60, "is_corner": False, "is_special": False},
    "Community Chest": {"value": 0, "is_corner": False, "is_special": True},
    "Baltic Avenue": {"value": 60, "is_corner": False, "is_special": False},
    "Income Tax": {"value": 0, "is_corner": False, "is_special": True},
    "Reading Railroad": {"value": 200, "is_corner": False, "is_special": False},
    "Oriental Avenue": {"value": 100, "is_corner": False, "is_special": False},
    "Chance": {"value": 0, "is_corner": False, "is_special": True},
    "Vermont Avenue": {"value": 100, "is_corner": False, "is_special": False},
    "Connecticut Avenue": {"value": 120, "is_corner": False, "is_special": False},
    
    "JAIL": {"value": 0, "is_corner": True, "is_special": True},
    "St. Charles Place": {"value": 140, "is_corner": False, "is_special": False},
    "Electric Company": {"value": 150, "is_corner": False, "is_special": False},
    "States Avenue": {"value": 140, "is_corner": False, "is_special": False},
    "Virginia Avenue": {"value": 160, "is_corner": False, "is_special": False},
    "Pennsylvania Railroad": {"value": 200, "is_corner": False, "is_special": False},
    "St. James Place": {"value": 180, "is_corner": False, "is_special": False},
    "Tennessee Avenue": {"value": 180, "is_corner": False, "is_special": False},
    "New York Avenue": {"value": 200, "is_corner": False, "is_special": False},
    "FREE PARKING": {"value": 0, "is_corner": True, "is_special": True},
    
    "Kentucky Avenue": {"value": 220, "is_corner": False, "is_special": False},
    "Indiana Avenue": {"value": 220, "is_corner": False, "is_special": False},
    "Illinois Avenue": {"value": 240, "is_corner": False, "is_special": False},
    "B&O Railroad": {"value": 200, "is_corner": False, "is_special": False},
    "Atlantic Avenue": {"value": 260, "is_corner": False, "is_special": False},
    "Ventnor Avenue": {"value": 260, "is_corner": False, "is_special": False},
    "Water Works": {"value": 150, "is_corner": False, "is_special": False},
    "Marvin Gardens": {"value": 280, "is_corner": False, "is_special": False},
    "GO TO JAIL": {"value": 0, "is_corner": True, "is_special": True},
    
    "Pacific Avenue": {"value": 300, "is_corner": False, "is_special": False},
    "North Carolina Avenue": {"value": 300, "is_corner": False, "is_special": False},
    "Pennsylvania Avenue": {"value": 320, "is_corner": False, "is_special": False},
    "Short Line Railroad": {"value": 200, "is_corner": False, "is_special": False},
    "Park Place": {"value": 350, "is_corner": False, "is_special": False},
    "Luxury Tax": {"value": 0, "is_corner": False, "is_special": True},
    "Boardwalk": {"value": 400, "is_corner": False, "is_special": False},
}

# Corner positions
CORNERS = {0: "GO", 10: "JAIL", 20: "FREE PARKING", 30: "GO TO JAIL"}

# Board rendering configuration
# Fixed corner size, properties scale dynamically based on board dimensions
BOARD_WIDTH = 940
BOARD_HEIGHT = 940
CORNER_SIZE = 110
# Properties calculated: (BOARD_WIDTH - 2*CORNER_SIZE) / 9 per side
PROPERTY_WIDTH = int((BOARD_WIDTH - 2 * CORNER_SIZE) / 9)
PROPERTY_HEIGHT = int((BOARD_HEIGHT - 2 * CORNER_SIZE) / 9)

# Colors
COLOR_BACKGROUND = (34, 139, 34)  # Forest green like real Monopoly
COLOR_CENTER = (245, 245, 220)  # Beige center
COLOR_BORDER = (0, 0, 0)
COLOR_TEXT = (0, 0, 0)
COLOR_PLAYER_1 = (220, 20, 60)  # Crimson red
COLOR_PLAYER_2 = (30, 144, 255)  # Dodger blue
COLOR_OWNED_BORDER = (255, 255, 255)
COLOR_PANEL_BG = (248, 248, 255)  # Ghost white
COLOR_LOG_BG = (255, 255, 255)  # White
COLOR_LOG_TEXT = (50, 50, 50)  # Dark gray

# Font sizes
FONT_SIZE_TITLE = 36
FONT_SIZE_LARGE = 22
FONT_SIZE_MEDIUM = 16
FONT_SIZE_SMALL = 12
FONT_SIZE_TINY = 10
