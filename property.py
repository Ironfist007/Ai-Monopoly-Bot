import random
from board_config import BOARD_LAYOUT


class Property:
    def __init__(self, name, value, position):
        self.name = name
        self.value = value
        self.position = position
        self.tax = 0
        self.rent = value * 0.1
        self.owner = None


# Property definitions matching actual board positions from BOARD_LAYOUT
# Format: (position, name, value)
PROPERTY_DEFINITIONS = [
    # Bottom row properties
    (1, "Mediterranean Avenue", 60),
    (3, "Baltic Avenue", 60),
    (5, "Reading Railroad", 200),
    (6, "Oriental Avenue", 100),
    (8, "Vermont Avenue", 100),
    (9, "Connecticut Avenue", 120),
    
    # Left side properties
    (11, "St. Charles Place", 140),
    (12, "Electric Company", 150),
    (13, "States Avenue", 140),
    (14, "Virginia Avenue", 160),
    (15, "Pennsylvania Railroad", 200),
    (16, "St. James Place", 180),
    (18, "Tennessee Avenue", 180),
    (19, "New York Avenue", 200),
    
    # Top row properties
    (21, "Kentucky Avenue", 220),
    (23, "Indiana Avenue", 220),
    (24, "Illinois Avenue", 240),
    (25, "B&O Railroad", 200),
    (26, "Atlantic Avenue", 260),
    (27, "Ventnor Avenue", 260),
    (28, "Water Works", 150),
    (29, "Marvin Gardens", 280),
    
    # Right side properties
    (31, "Pacific Avenue", 300),
    (32, "North Carolina Avenue", 300),
    (34, "Pennsylvania Avenue", 320),
    (35, "Short Line Railroad", 200),
    (37, "Park Place", 350),
    (39, "Boardwalk", 400),
]

properties = []

# Randomly select 5 properties to have tax
property_names_for_tax = [p[1] for p in PROPERTY_DEFINITIONS]
properties_with_tax = random.sample(property_names_for_tax, 5)

# Create property objects with correct board positions
for position, name, value in PROPERTY_DEFINITIONS:
    property_obj = Property(name, value, position)
    if name in properties_with_tax:
        property_obj.tax = random.randint(10, 50)
    properties.append(property_obj)
