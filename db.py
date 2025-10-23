"""
NICE-BOT - Database Management
SQLite database setup and operations
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join("data", "bot.db")

def init_database():
    """Initialize the SQLite database and create tables"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'fr',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            input TEXT,
            output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Gamification tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            xp_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            total_commands INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_activity DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT,
            xp_required INTEGER DEFAULT 0,
            special_condition TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (badge_id) REFERENCES badges (id),
            UNIQUE(user_id, badge_id)
        )
    ''')
    
    conn.commit()
    
    # Initialize default badges
    init_default_badges(cursor)
    conn.commit()
    
    conn.close()
    logger.info("Database tables created successfully")

def init_default_badges(cursor):
    """Initialize default badges"""
    default_badges = [
        ("🚀 Débutant", "Première commande utilisée", "🚀", 0, "first_command"),
        ("⚡ Actif", "10 commandes utilisées", "⚡", 50, None),
        ("🔥 Passionné", "50 commandes utilisées", "🔥", 250, None),
        ("💎 Expert", "100 commandes utilisées", "💎", 500, None),
        ("👑 Maître", "500 commandes utilisées", "👑", 2500, None),
        ("🌟 Légende", "1000 commandes utilisées", "🌟", 5000, None),
        ("🤖 IA Lover", "Utilisé 10 commandes IA", "🤖", 100, "ai_commands"),
        ("🌍 Traducteur", "Utilisé 20 traductions", "🌍", 100, "translate_commands"),
        ("🎮 Joueur", "Utilisé 15 commandes fun", "🎮", 75, "fun_commands"),
        ("📊 Analyste", "Consulté les stats 5 fois", "📊", 50, "stats_commands"),
        ("🔥 Série", "7 jours consécutifs d'activité", "🔥", 200, "streak_7"),
        ("💪 Persévérant", "30 jours consécutifs", "💪", 1000, "streak_30")
    ]
    
    for badge in default_badges:
        cursor.execute('''
            INSERT OR IGNORE INTO badges (name, description, icon, xp_required, special_condition)
            VALUES (?, ?, ?, ?, ?)
        ''', badge)

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def add_user(telegram_id: str, username: Optional[str] = None, first_name: Optional[str] = None) -> bool:
    """Add a new user to the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, first_name))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

def get_user(telegram_id: str) -> Optional[Dict[str, Any]]:
    """Get user information by telegram_id"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, telegram_id, username, first_name, language, joined_at
            FROM users WHERE telegram_id = ?
        ''', (telegram_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'telegram_id': row[1],
                'username': row[2],
                'first_name': row[3],
                'language': row[4],
                'joined_at': row[5]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None

def add_history(user_id: int, command: str, input_text: str = "", output_text: str = "") -> bool:
    """Add command history entry"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO history (user_id, command, input, output)
            VALUES (?, ?, ?, ?)
        ''', (user_id, command, input_text, output_text))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding history: {e}")
        return False

def get_user_stats() -> Dict[str, int]:
    """Get user and command statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Get total commands
        cursor.execute("SELECT COUNT(*) FROM history")
        total_commands = cursor.fetchone()[0]
        
        return {
            'total_users': total_users,
            'total_commands': total_commands
        }
    finally:
        conn.close()

def get_all_users():
    """Get all users from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT telegram_id, username, first_name, language, joined_at 
            FROM users 
            ORDER BY joined_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'telegram_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'language': row[3],
                'joined_at': row[4]
            })
        
        return users
    finally:
        conn.close()

def get_recent_history(limit=20):
    """Get recent command history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT h.user_id, h.command, h.created_at, u.first_name
            FROM history h
            LEFT JOIN users u ON h.user_id = u.id
            ORDER BY h.created_at DESC
            LIMIT ?
        """, (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'user_id': row[0],
                'command': row[1],
                'created_at': row[2],
                'first_name': row[3]
            })
        
        return history
    finally:
        conn.close()

def get_recent_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent command history for logs"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT h.command, h.input, h.created_at, u.username, u.first_name
            FROM history h
            JOIN users u ON h.user_id = u.id
            ORDER BY h.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'command': row[0],
                'input': row[1],
                'created_at': row[2],
                'username': row[3],
                'first_name': row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        return []

def get_recent_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent command history for admin panel"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT h.user_id, h.command, h.created_at
            FROM history h
            ORDER BY h.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'user_id': row[0],
                'command': row[1],
                'created_at': row[2]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting recent history: {e}")
        return []
