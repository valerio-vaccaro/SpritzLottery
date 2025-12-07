# SpritzLottery

A provable random lottery game based on Bitcoin block nonces. Predict the nonce of future Bitcoin blocks and compete with others!

## 🎯 Overview

SpritzLottery is a web application that allows users to create prediction games based on Bitcoin block nonces. Participants submit their predictions for the nonce of a future block, and the closest prediction wins!

### Features

- 🎮 **Create Games**: Set a target block height and start a new prediction game
- 📊 **Submit Predictions**: Participants can submit their nonce predictions (hexadecimal format)
- 📈 **Real-time Updates**: Automatic refresh for active games
- 📱 **QR Code Sharing**: Share games easily via QR codes
- 📊 **Distribution Charts**: Visual representation of prediction distribution
- 🏆 **Global Leaderboard**: See the best predictions across all finished games
- 🎨 **Participant Emojis**: Each participant gets a unique emoji based on their name
- 🔗 **Blockstream Integration**: Direct links to view blocks on Blockstream.info

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SpritzLottery
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Starting the Application

Run the Flask application:
```bash
python app.py
```

The application will be available at `http://localhost:5000` (or `http://127.0.0.1:5000`).

### Creating a Game

1. Navigate to the home page
2. Click "Create New Game"
3. Enter a target block height (must be at least 2 blocks in the future)
4. The game will be created and you'll be redirected to the game page

### Submitting Predictions

1. Go to a game page (must be in "active" status)
2. Click "Add/Update Your Prediction"
3. Enter your name (unique identifier) and your nonce prediction
4. Submit the form

**Nonce Format**: Accepts hexadecimal format with or without `0x` prefix, with or without padding:
- `ffff`
- `0xffff`
- `0000ffff`
- `1234ABCD`

**Valid Range**: `0x00000000` to `0xFFFFFFFF` (32-bit unsigned integer)

### Game Lifecycle

1. **Active**: Predictions can be submitted
2. **Closed**: Predictions are closed, waiting for the target block
3. **Finished**: The game is complete, winner determined by smallest distance

## 📁 Project Structure

```
SpritzLottery/
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── games.db              # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── index.html        # Home page with games list and leaderboard
│   ├── create.html       # Create new game page
│   ├── game.html         # Game details page
│   └── guess.html        # Submit prediction page
└── README.md             # This file
```

## 🗄️ Database Schema

### Games Table
- `game_id` (TEXT, PRIMARY KEY): Unique game identifier
- `target_height` (INTEGER): Target block height
- `status` (TEXT): Game status (active, closed, finished)
- `real_nonce` (INTEGER): Actual nonce from the target block
- `block_hash` (TEXT): Hash of the target block
- `block_time` (TEXT): Timestamp of the target block

### Guesses Table
- `game_id` (TEXT): Foreign key to games
- `name` (TEXT): Participant name
- `guess` (INTEGER): Predicted nonce value
- `timestamp` (DATETIME): When the prediction was submitted
- `distance` (INTEGER): Distance from actual nonce (calculated after game finishes)
- PRIMARY KEY: (`game_id`, `name`)

## 🔧 Configuration

### Bitcoin API

The application uses `blockchain.info` API to fetch block information:
- Current block height: `https://blockchain.info/q/getblockcount`
- Latest block: `https://blockchain.info/latestblock`
- Block info: `https://blockchain.info/block-height/{height}?format=json`

### Background Process

A background thread runs every 60 seconds to:
- Check for games that need status updates
- Close games when approaching target block
- Finalize games when target block is mined
- Calculate distances for all predictions

## 🎨 Features Details

### Participant Emojis

Each participant gets a unique emoji based on their name hash. The same name will always get the same emoji, making it easy to identify participants across games.

### Distribution Chart

The prediction distribution chart shows how predictions are spread across the nonce range, helping visualize the competition.

### Global Leaderboard

The global leaderboard shows the top 100 predictions across all finished games, sorted by distance (smaller is better).

### QR Code Sharing

Each game page includes a QR code that links directly to the game, making it easy to share with participants.

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or issues, please open an issue on the repository.

---

**Note**: This application is for educational and entertainment purposes. Always verify block information independently.
