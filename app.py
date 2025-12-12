# app.py
# Versione aggiornata con:
# - Lista di tutti i giochi (passati e futuri) in index con link.
# - Pagina separata per aggiungere stime: /game/<id>/guess (con form).
# - Bottone nella pagina del gioco per andare alla pagina guess.
# - Refresh automatico ogni 10 secondi nella pagina del gioco (solo se active o closed, via JS).

from flask import Flask, request, render_template, redirect, url_for, abort, flash, jsonify
import sqlite3
import requests
from datetime import datetime
import threading
import time
import uuid
import re
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # per flash messages

# Get domain from environment variable, default to production URL
DOMAIN = os.environ.get('SPRITZLOTTERY_DOMAIN', 'https://lottery.satoshispritz.it')

# Range nonce Bitcoin (32 bit)
NONCE_MIN = 0
NONCE_MAX = 0xFFFFFFFF  # 4294967295

def hex_to_int(hex_str):
    """Convert hex string to integer, accepting formats like 'ffff', '0xffff', '0000ffff', etc."""
    try:
        # Remove 0x prefix if present
        hex_str = hex_str.strip()
        if hex_str.lower().startswith('0x'):
            hex_str = hex_str[2:]
        # Remove leading zeros (but keep at least one digit)
        hex_str = hex_str.lstrip('0') or '0'
        # Convert to int (max 8 hex digits = 32 bits)
        if len(hex_str) > 8:
            return None
        return int(hex_str, 16)
    except (ValueError, AttributeError):
        return None

def int_to_hex(n):
    return f"0x{n:08x}".upper()

# List of emojis for participants (common emojis well-supported by browsers)
PARTICIPANT_EMOJIS = [
    '🎯', '🚀', '⭐', '🔥', '💎', '🎲', '🎪', '🎨', '🎭', '🎬',
    '🏆', '🥇', '🥈', '🥉', '🎖️', '🏅', '🎗️', '🎟️', '🎫', '🎴',
    '🃏', '🀄', '🎰', '🎮', '🕹️', '🎳', '🎱', '🏓', '🏸', '⚽',
    '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🌍', '🌎', '🌏', '🌐',
    '🗺️', '🧭', '🏔️', '⛰️', '🌋', '🗻', '🏕️', '🏖️', '🏜️', '🏝️',
    '🏞️', '🏟️', '🏛️', '🏗️', '🏘️', '🏚️', '🏠', '🏡', '🏢', '🏣',
    '🏤', '🏥', '🏦', '🏨', '🏩', '🦄', '🐉', '🐲', '🦁', '🐯',
    '🐰', '🐻', '🐼', '🐨', '🐵', '🦊', '🐺', '🐗', '🐴', '🦓',
    '🦌', '🐮', '🐷', '🐽', '🐸', '🐊', '🐢', '🦎', '🐍', '🦕',
    '🦖', '🐳', '🐋', '🐬', '🐟', '🐠', '🐡', '🦈', '🐙', '🐚',
    '🐌', '🦋', '🐛', '🐜', '🐝', '🐞', '🦗', '🕷️', '🦂', '🦟',
    '💐', '🌸', '💮', '🏵️', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷',
    '🌱', '🌲', '🌳', '🌴', '🌵', '🌶️', '🌾', '🌿', '☘️', '🍀',
    '🍁', '🍂', '🍃', '🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍',
    '🥭', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🥝', '🍅', '🥥',
    '🥑', '🍆', '🥔', '🥕', '🌽', '🥒', '🥬', '🥦', '🥗', '🥘',
    '🥙', '🥚', '🥛', '🥜', '🥞', '🥟', '🥠', '🥡', '🥢', '🥣',
    '🥤', '🥧', '🥨', '🥩', '🥪', '🥫', '🥮', '🥯', '🥰', '🥱',
    '🥲', '🥳', '🥴', '🥵', '🥶', '🥷', '🥸', '🥹', '🥺', '🦀',
    '🦂', '🦃', '🦄', '🦅', '🦆', '🦇', '🦈', '🦉', '🦊', '🦋',
    '🦌', '🦍', '🦎', '🦏', '🦐', '🦑', '🦒', '🦓', '🦔', '🦕',
    '🦖', '🦗', '🦘', '🦙', '🦚', '🦛', '🦜', '🦝', '🦞', '🦟',
    '🦡', '🦢', '🧀', '🧁', '🧂', '🧃', '🧄', '🧅', '🧆', '🧇',
    '🧈', '🧉', '🧊', '🧋', '🧍', '🧎', '🧏', '🧐', '🧑', '🧒',
    '🧓', '🧔', '🧕', '🧖', '🧗', '🧘', '🧙', '🧚', '🧛', '🧜',
    '🧝', '🧞', '🧟', '🧠', '🧡', '🧢', '🧣', '🧤', '🧥', '🧦',
    '🧧', '🧨', '🧩', '🧪', '🧫', '🧬', '🧭', '🧮', '🧯', '🧰',
    '🧱', '🧲', '🧳', '🧴', '🧵', '🧶', '🧷', '🧸', '🧹', '🧺',
    '🧻', '🧼', '🧽', '🧾', '🧿', '🩰', '🩱', '🩲', '🩳', '🩴',
    '🩵', '🩶', '🩷', '🩸', '🩹', '🩺', '🪀', '🪁', '🪂', '🪃',
    '🪄', '🪅', '🪆', '🪇', '🪈', '🪉', '🪊', '🪋', '🪌', '🪍',
    '🪎', '🪏', '🪐', '🪑', '🪒', '🪓', '🪔', '🪕', '🪖', '🪗',
    '🪘', '🪙', '🪚', '🪛', '🪜', '🪝', '🪞', '🪟', '🪠', '🪡',
    '🪢', '🪣', '🪤', '🪥', '🪦', '🪧', '🪨', '🪩', '🪪', '🪫',
    '🪬', '🪭', '🪮', '🪯', '🪰', '🪱', '🪲', '🪳', '🪴', '🪵',
    '🪶', '🪷', '🪸', '🪹', '🪺', '🪻', '🪼', '🪽', '🪾', '🪿',
    '🫀', '🫁', '🫂', '🫃', '🫄', '🫅', '🫆', '🫇', '🫈', '🫉',
    '🫊', '🫋', '🫌', '🫍', '🫎', '🫏', '🫐', '🫑', '🫒', '🫓',
    '🫔', '🫕', '🫖', '🫗', '🫘', '🫙', '🫚', '🫛', '🫜', '🫝',
    '🫞', '🫟', '🫠', '🫡', '🫢', '🫣', '🫤', '🫥', '🫦', '🫧',
    '🫨', '🫩', '🫪', '🫫', '🫬', '🫭', '🫮', '🫯', '🫰', '🫱',
    '🫲', '🫳', '🫴', '🫵', '🫶', '🫷', '🫸', '🫹', '🫺', '🫻',
    '🫼', '🫽', '🫾', '🫿'
]

def get_participant_emoji(name):
    """Get a consistent emoji for a participant based on their name."""
    if not name:
        return '👤'
    # Use hash of name to get consistent emoji
    hash_value = hash(name)
    emoji_index = abs(hash_value) % len(PARTICIPANT_EMOJIS)
    return PARTICIPANT_EMOJIS[emoji_index]

# Register Jinja2 template globals
app.jinja_env.globals['int_to_hex'] = int_to_hex
app.jinja_env.globals['enumerate'] = enumerate
app.jinja_env.globals['get_participant_emoji'] = get_participant_emoji

# API Bitcoin
def get_current_block_height():
    try:
        r = requests.get('https://blockchain.info/q/getblockcount', timeout=10)
        return int(r.text)
    except:
        return None

def get_block_info(height):
    try:
        r = requests.get(f'https://blockchain.info/block-height/{height}?format=json', timeout=10)
        block = r.json()['blocks'][0]
        return (
            block['nonce'],
            block['hash'],
            datetime.fromtimestamp(block['time'])
        )
    except:
        return None, None, None

def get_latest_block_info():
    try:
        r = requests.get('https://blockchain.info/latestblock', timeout=10)
        data = r.json()
        height = data['height']
        nonce, hash_, time_ = get_block_info(height)
        return height, hash_, time_, nonce
    except:
        return None, None, None, None

# Hash PIN function
def hash_pin(pin):
    """Hash a PIN using SHA256"""
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin, pin_hash):
    """Verify a PIN against its hash"""
    return hash_pin(pin) == pin_hash

# DB init
def init_db():
    conn = sqlite3.connect('games.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (game_id TEXT PRIMARY KEY, target_height INTEGER, status TEXT,
                  real_nonce INTEGER, block_hash TEXT, block_time TEXT, pin_hash TEXT)''')
    # Add pin_hash column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE games ADD COLUMN pin_hash TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    c.execute('''CREATE TABLE IF NOT EXISTS guesses
                 (game_id TEXT, name TEXT, guess INTEGER, timestamp DATETIME, distance INTEGER,
                  PRIMARY KEY (game_id, name))''')
    conn.commit()
    conn.close()

init_db()

# Background checker
def check_games():
    while True:
        current = get_current_block_height()
        if not current:
            time.sleep(60)
            continue

        conn = sqlite3.connect('games.db')
        c = conn.cursor()
        c.execute("SELECT game_id, target_height, status FROM games WHERE status != 'finished'")
        games = c.fetchall()

        for game_id, target, status in games:
            if current >= target - 1 and status == 'active':
                c.execute("UPDATE games SET status = 'closed' WHERE game_id = ?", (game_id,))
            if current >= target and status in ('active', 'closed'):
                nonce, hash_, time_ = get_block_info(target)
                if nonce is not None:
                    time_str = time_.strftime("%Y-%m-%d %H:%M:%S")
                    c.execute('''UPDATE games SET real_nonce = ?, block_hash = ?, block_time = ?, status = 'finished'
                                 WHERE game_id = ?''', (nonce, hash_, time_str, game_id))
                    c.execute("SELECT name, guess FROM guesses WHERE game_id = ?", (game_id,))
                    for name, guess in c.fetchall():
                        dist = abs(guess - nonce)
                        c.execute("UPDATE guesses SET distance = ? WHERE game_id = ? AND name = ?", (dist, game_id, name))
        conn.commit()
        conn.close()
        time.sleep(60)

threading.Thread(target=check_games, daemon=True).start()

@app.route('/')
def index():
    conn = sqlite3.connect('games.db')
    c = conn.cursor()
    # Get games with prediction count
    c.execute('''SELECT g.game_id, g.target_height, g.status, 
                        COUNT(gu.name) as prediction_count
                 FROM games g
                 LEFT JOIN guesses gu ON g.game_id = gu.game_id
                 GROUP BY g.game_id, g.target_height, g.status
                 ORDER BY g.target_height DESC''')
    games = c.fetchall()
    
    # Get global leaderboard: all participants from finished games, ordered by distance
    c.execute('''SELECT g.game_id, g.target_height, gu.name, gu.guess, gu.distance, gu.timestamp
                  FROM games g
                  INNER JOIN guesses gu ON g.game_id = gu.game_id
                  WHERE g.status = 'finished' AND gu.distance IS NOT NULL
                  ORDER BY gu.distance ASC, gu.timestamp ASC
                  LIMIT 100''')
    leaderboard = c.fetchall()
    
    conn.close()

    latest = get_latest_block_info()
    return render_template('index.html', games=games, latest=latest, leaderboard=leaderboard,
                           nonce_min=int_to_hex(NONCE_MIN),
                           nonce_max=int_to_hex(NONCE_MAX))

@app.route('/create', methods=['GET', 'POST'])
def create_game():
    if request.method == 'POST':
        try:
            target = int(request.form['target_height'])
            pin = request.form.get('pin', '').strip()
            current = get_current_block_height() or 0
            MAX_BLOCKS_AHEAD = 144 * 7  # One week (144 blocks per day * 7 days)
            
            if not pin:
                flash("PIN is required!", "danger")
            elif len(pin) < 4:
                flash("PIN must be at least 4 characters long!", "danger")
            elif target <= current + 1:
                flash("The height must be at least 2 blocks in the future!", "danger")
            elif target > current + MAX_BLOCKS_AHEAD:
                flash(f"The target height cannot be more than {MAX_BLOCKS_AHEAD} blocks ({MAX_BLOCKS_AHEAD // 144} days) in the future! Maximum allowed: {current + MAX_BLOCKS_AHEAD}", "danger")
            else:
                game_id = str(uuid.uuid4())[:8]  # Short ID
                pin_hash = hash_pin(pin)
                conn = sqlite3.connect('games.db')
                c = conn.cursor()
                c.execute("INSERT INTO games (game_id, target_height, status, pin_hash) VALUES (?, ?, 'active', ?)",
                          (game_id, target, pin_hash))
                conn.commit()
                conn.close()
                flash("Game created successfully! Remember your PIN - it will be needed for predictions.", "success")
                return redirect(url_for('game', game_id=game_id))
        except ValueError:
            flash("Invalid target height!", "danger")
        except Exception as e:
            flash(f"Error creating the game: {str(e)}", "danger")
    latest = get_latest_block_info()
    current_height = latest[0] if latest and latest[0] is not None else 0
    MAX_BLOCKS_AHEAD = 144 * 7  # One week (144 blocks per day * 7 days)
    max_target = current_height + MAX_BLOCKS_AHEAD
    return render_template('create.html', latest=latest,
                           nonce_min=int_to_hex(NONCE_MIN),
                           nonce_max=int_to_hex(NONCE_MAX),
                           max_target=max_target,
                           max_blocks_ahead=MAX_BLOCKS_AHEAD)

@app.route('/game/<game_id>', methods=['GET'])
def game(game_id):
    conn = sqlite3.connect('games.db')
    c = conn.cursor()
    c.execute("SELECT target_height, status, real_nonce, block_hash, block_time, pin_hash FROM games WHERE game_id = ?", (game_id,))
    game_data = c.fetchone()
    if not game_data:
        abort(404)

    target_height, status, real_nonce, block_hash, block_time, pin_hash = game_data

    # Recupera stime
    if status == 'finished':
        c.execute('''SELECT name, guess, timestamp, distance FROM guesses
                     WHERE game_id = ? ORDER BY distance ASC, timestamp ASC''', (game_id,))
    else:
        c.execute('''SELECT name, guess, timestamp FROM guesses
                     WHERE game_id = ? ORDER BY guess ASC''', (game_id,))
    guesses_raw = c.fetchall()
    guesses = [(n, int_to_hex(g), t, d if status == 'finished' else None) for n, g, t, *d in guesses_raw]  # Adatta per 3 o 4 colonne

    winner = guesses[0][0] if guesses and status == 'finished' else None
    real_nonce_hex = int_to_hex(real_nonce) if real_nonce else None

    # Prepare data for distribution chart
    guess_values = [g[1] for g in guesses] if guesses else []  # Hex values
    guess_ints = [hex_to_int(g) for g in guess_values if hex_to_int(g) is not None]  # Integer values

    conn.close()
    latest = get_latest_block_info()
    
    # Generate full URL for QR code using domain from environment variable
    game_url = f"{DOMAIN}{url_for('game', game_id=game_id)}"

    return render_template('game.html',
                           game_id=game_id,
                           target_height=target_height,
                           status=status,
                           real_nonce_hex=real_nonce_hex,
                           block_hash=block_hash,
                           block_time=block_time,
                           guesses=guesses,
                           guess_ints=guess_ints,
                           winner=winner,
                           latest=latest,
                           game_url=game_url,
                           nonce_min=int_to_hex(NONCE_MIN),
                           nonce_max=int_to_hex(NONCE_MAX))

@app.route('/game/<game_id>/guess', methods=['GET', 'POST'])
def game_guess(game_id):
    conn = sqlite3.connect('games.db')
    c = conn.cursor()
    c.execute("SELECT target_height, status, pin_hash FROM games WHERE game_id = ?", (game_id,))
    game_data = c.fetchone()
    if not game_data:
        abort(404)

    target_height, status, pin_hash = game_data

    if status != 'active':
        flash("The game is not active, you cannot add predictions!", "danger")
        conn.close()
        return redirect(url_for('game', game_id=game_id))

    if request.method == 'POST':
        # Normalize name: lowercase and remove all spaces
        name = request.form['name'].strip().lower().replace(' ', '')
        hex_guess = request.form['guess'].strip()
        pin = request.form.get('pin', '').strip()

        if not name:
            flash("Name is required!", "danger")
        elif not pin:
            flash("PIN is required!", "danger")
        elif not verify_pin(pin, pin_hash):
            flash("Invalid PIN! Please check your PIN and try again.", "danger")
        elif not re.match(r'^(0x)?[0-9a-fA-F]{1,8}$', hex_guess, re.IGNORECASE):
            flash("Invalid hexadecimal format! You can use 'ffff', '0xffff', '0000ffff', etc.", "danger")
        else:
            guess_int = hex_to_int(hex_guess)
            if guess_int is None or not (NONCE_MIN <= guess_int <= NONCE_MAX):
                flash(f"Nonce must be between {int_to_hex(NONCE_MIN)} and {int_to_hex(NONCE_MAX)}", "danger")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''INSERT OR REPLACE INTO guesses (game_id, name, guess, timestamp, distance)
                             VALUES (?, ?, ?, ?, NULL)''', (game_id, name, guess_int, timestamp))
                conn.commit()
                flash("Prediction updated successfully!", "success")
                conn.close()
                return redirect(url_for('game', game_id=game_id))

    conn.close()
    return render_template('guess.html',
                           game_id=game_id,
                           target_height=target_height,
                           nonce_min=int_to_hex(NONCE_MIN),
                           nonce_max=int_to_hex(NONCE_MAX))

if __name__ == '__main__':
    app.run(debug=True)
