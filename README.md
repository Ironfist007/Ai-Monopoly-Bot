# AI Monopoly Game - Visual AI Battle

A visual AI-powered Monopoly game where you can watch two intelligent AI players compete against each other using the Expectiminimax algorithm. The game features a responsive 2D Monopoly board with real-time game logging and strategic AI decision-making.

## Features

- **AI vs AI Gameplay**: Watch two AI players make strategic decisions automatically
- **Visual 2D Board**: Classic 40-space Monopoly board layout with color-coded properties
- **Real-time Game Log**: Detailed log of all AI decisions, dice rolls, and transactions
- **Responsive Board**: Dynamically resizes to fit your screen
- **Property Management**: Full property ownership, rent collection, and buying/selling mechanics
- **Jail Mechanics**: Proper jail logic with automatic release after 3 turns
- **Player Tracking**: Real-time display of player positions, balances, and property holdings
- **Speed Control**: Adjust game speed with a slider to watch at your preferred pace
- **Pause/Resume**: Pause the game to analyze moves, then resume
- **Dice Visualization**: Visual representation of dice rolls

## Game Modes

### AI Automatic Mode (Main)
- **File**: `ai_monopoly_gui.py`
- **Start**: `python ai_monopoly_gui.py`
- Two AI players automatically play against each other
- Uses Expectiminimax algorithm for intelligent decision-making
- Watch AI strategically buy properties and manage cash flow
- Real-time visualization of all game events

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
python ai_monopoly_gui.py
```

### 2. Control the AI Battle
- **Start AI Game**: Begin the automatic AI vs AI match
- **Game Speed**: Use the slider to control how fast the game plays (0.5x to 5.0x)
- **Pause**: Pause the game to examine the board and decisions
- **Resume**: Resume the game from where it was paused
- **Reset Game**: Start a new game from the beginning

### 3. Watch the Action
- **Game Log**: See all AI decisions, dice rolls, and property transactions
- **Board Updates**: Properties change color as players acquire them
- **Player Info**: Track each AI player's balance, properties, and current position
- **Dice Roll**: View the current dice result

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
├── ai_monopoly_gui.py       # Main AI GUI application
├── game.py                  # Game logic and flow
├── node.py                  # Expectiminimax node structure
├── tree.py                  # Game tree generation and evaluation
├── player.py                # Player class with properties and balance
├── property.py              # Property definitions and management
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Requirements

- Python 3.6+
- tkinter (included with most Python installations)
- No external packages required

## Game Rules Implemented

- **Starting Balance**: $1500 per player
- **Property Purchase**: Players can buy unowned properties they land on
- **Rent**: Landing on owned property requires paying rent to owner
- **Go Salary**: $200 for passing or landing on GO
- **Jail**: Players sent to JAIL at space 30, released after 3 turns or by paying $50
- **Win Condition**: First player to $2000+ wins, or opponent goes bankrupt
- **AI Decisions**: Buy properties, sell if in danger, collect rent, manage cash risk

## Configuration

Edit `ai_monopoly_gui.py` to adjust:
- Initial board size: `initial_board` variable
- AI intelligence level: `intelligence_level` in `run_ai_game()`
- Max game moves: `max_moves` variable
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
- **Author**: Ironfist007

## License

Open source - feel free to study, modify, and extend!
