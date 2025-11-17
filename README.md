# AI Monopoly Game - Pygame AI Battle

A Pygame-powered visual AI Monopoly game where you can watch two intelligent AI players compete against each other using the Expectiminimax algorithm. The game features a professional 2D Monopoly board with real-time game logging, strategic AI decision-making, and smooth animations.

## Features

- **AI vs AI Gameplay**: Watch two AI players make strategic decisions automatically
- **Visual 2D Board**: Classic 40-space Monopoly board layout with color-coded properties
- **Real-time Game Log**: Detailed log of all AI decisions, dice rolls, and transactions
- **Optimized Screen Fit**: Scaled board (740x740) that fits on standard 1080p displays
- **Property Management**: Full property ownership, rent collection, and buying/selling mechanics
- **Jail Mechanics**: Proper jail logic with automatic release after 3 turns
- **Player Tracking**: Real-time display of player positions (Player 1 & 2), balances, and property holdings
- **Speed Control**: Adjust game speed with a slider to watch at your preferred pace (0.2s to 3.0s)
- **Pause/Resume**: Pause the game to analyze moves, then resume
- **Scrollable Game Log**: Full game history with mouse/keyboard scrolling - now scrolls all the way to bottom
- **Property Prices**: Visible property purchase prices in black text on board
- **Property Ownership Colors**: Visual property ownership indicators at top of each property
- **Smooth Animations**: Professional game piece movement and UI transitions
- **Dual Panel Layout**: Board view and AI insights panel side-by-side

## Game Modes

### AI Automatic Mode (Main)
- **File**: `ai_monopoly_pygame.py`
- **Start**: `python ai_monopoly_pygame.py`
- Two AI players automatically play against each other
- Uses Expectiminimax algorithm for intelligent decision-making
- Watch AI strategically buy properties and manage cash flow
- Real-time visualization of all game events

## Recent Updates (UI Improvements)

### v2.0 - Enhanced User Experience
- **Optimized Screen Size**: Board scaled from 940x940 to 740x740 pixels for better fit on standard displays
- **Improved Panel Layout**: Right panel reduced to 420px width for better proportions
- **Fixed Log Scrolling**: Game log now scrolls smoothly to the very bottom without getting stuck
- **Better Player Labels**: Display shows "Player 1" and "Player 2" instead of "Player 0" and "Player 1"
- **Property Prices Visible**: All property purchase prices now display in black text (previously hidden)
- **Reduced Font Sizes**: Optimized typography for the smaller board while maintaining readability

## Algorithm: Expectiminimax

The AI uses the **Expectiminimax algorithm**, an extension of Minimax that handles probabilistic events:
- **Decision Nodes**: AI chooses best action (buy/sell/do nothing) to maximize expected utility
- **Chance Nodes**: Dice rolls (1-6) are evaluated probabilistically
- **Utility Function**: Evaluates player strength based on:
  - Property value and rent potential
  - Current cash balance
  - Risk assessment (prevents bankruptcy)
  - Strategic depth (configurable intelligence level)

## How to Play (Watch AI)

### 1. Start the Game
```bash
python ai_monopoly_pygame.py
```

### 2. Control the AI Battle
- **START Button**: Begin the automatic AI vs AI match
- **PAUSE/RESUME Button**: Pause to examine moves, resume to continue
- **RESET Button**: Start a new game from the beginning
- **Speed Slider**: Control game pace from 0.2s to 3.0s per move
- **Game Log Scrolling**: Use mouse wheel or arrow keys to scroll through history

### 3. Watch the Action
- **Game Log**: See all AI decisions, dice rolls, and property transactions
- **Board Updates**: Properties change color as players acquire them  
- **Player Stats**: Real-time balance, property count, position, and risk assessment
- **Utility Scores**: AI evaluation scores showing decision quality

### 4. Keyboard Controls
- **SPACE**: Pause/Resume game
- **ESC**: Exit game
- **↑/↓ Arrow Keys**: Scroll game log
- **Mouse Wheel**: Scroll game log

## Board Layout

- **40 Spaces**: Classic Monopoly arrangement
- **Corners**: GO, JAIL, FREE PARKING, GO TO JAIL
- **Property Sides**:
  - Bottom: Mediterranean Ave to Connecticut Ave (brown to light blue)
  - Left: St. Charles to New York Ave (pink to orange)
  - Top: Kentucky to Marvin Gardens (red to yellow)
  - Right: Pacific to Boardwalk (green to dark blue)
- **Special Spaces**: Community Chest, Chance, Income Tax, Luxury Tax

## Project Structure

```
.
├── ai_monopoly_pygame.py    # Main Pygame GUI application
├── board_config.py          # Board layout and visual configuration
├── game.py                  # Game logic and flow
├── node.py                  # Expectiminimax node structure
├── tree.py                  # Game tree generation and evaluation
├── player.py                # Player class with properties and balance
├── property.py              # Property definitions and management
├── .gitignore               # Git ignore file
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Requirements

- Python 3.8+
- pygame>=2.0.0

Install dependencies:
```bash
pip install -r requirements.txt
```

Or install pygame directly:
```bash
pip install pygame
```

## Game Rules Implemented

- **Starting Balance**: $1500 per player
- **Property Purchase**: Players can buy unowned properties they land on
- **Rent**: Landing on owned property requires paying rent to owner
- **Go Salary**: $200 for passing or landing on GO
- **Jail**: Players sent to JAIL at space 30, released after 3 turns or by paying $50
- **Win Condition**: First player to $2000+ wins, or opponent goes bankrupt
- **AI Decisions**: Buy properties, sell if in danger, collect rent, manage cash risk

## Configuration

Edit `ai_monopoly_pygame.py` to adjust:
- Board dimensions: `BOARD_WIDTH`, `BOARD_HEIGHT` in `board_config.py`
- AI intelligence level: `intelligence_level` in `_run_game_loop()`
- Max game moves: `max_moves` variable
- Game speed: `self.game_speed` range (0.2 to 3.0 seconds)
- Starting balance: Modify `Player(0, balance=1500)` calls

## Tips for Watching

1. Start with slower speed (0.5x) to see detailed decisions
2. Use Pause to read the game log and analyze AI moves
3. Watch how AI adjusts strategy:
   - Early game: Aggressive property buying
   - Mid game: Strategic rent collection
   - Late game: Cash management and asset positioning
4. Higher intelligence level = better decisions but slower computation

## Credits

- **AI Algorithm**: Expectiminimax implementation for turn-based games with chance
- **Project**: AI Monopoly Game - Educational demonstration of game-playing AI

## License

Open source - feel free to study, modify, and extend!
