#!/usr/bin/env python3
"""
Gamification System for NICE-BOT
XP points, levels, badges, and achievements
"""

import logging
import sqlite3
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_connection

logger = logging.getLogger(__name__)

# XP values for different actions
XP_VALUES = {
    'command_use': 5,
    'daily_bonus': 10,
    'streak_bonus': 5,
    'first_time': 20,
    'special_command': 15
}

# Level thresholds
LEVEL_THRESHOLDS = [0, 50, 150, 300, 500, 750, 1100, 1500, 2000, 2600, 3300, 4100, 5000]

def get_user_stats(user_id: int):
    """Get user gamification stats"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT xp_points, level, total_commands, streak_days, last_activity
            FROM user_stats WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'xp_points': result[0],
                'level': result[1],
                'total_commands': result[2],
                'streak_days': result[3],
                'last_activity': result[4]
            }
        else:
            # Create new stats entry
            cursor.execute('''
                INSERT INTO user_stats (user_id, xp_points, level, total_commands, streak_days, last_activity)
                VALUES (?, 0, 1, 0, 0, ?)
            ''', (user_id, date.today().isoformat()))
            conn.commit()
            return {
                'xp_points': 0,
                'level': 1,
                'total_commands': 0,
                'streak_days': 0,
                'last_activity': date.today().isoformat()
            }
    finally:
        conn.close()

def add_xp(user_id: int, xp_amount: int, command: str = None):
    """Add XP to user and check for level up"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        stats = get_user_stats(user_id)
        new_xp = stats['xp_points'] + xp_amount
        new_level = calculate_level(new_xp)
        
        # Update streak
        today = date.today()
        last_activity = datetime.strptime(stats['last_activity'], '%Y-%m-%d').date()
        
        if today == last_activity:
            # Same day, no streak change
            new_streak = stats['streak_days']
        elif today == last_activity + timedelta(days=1):
            # Consecutive day
            new_streak = stats['streak_days'] + 1
        else:
            # Streak broken
            new_streak = 1
        
        # Update stats
        cursor.execute('''
            UPDATE user_stats 
            SET xp_points = ?, level = ?, total_commands = total_commands + 1, 
                streak_days = ?, last_activity = ?
            WHERE user_id = ?
        ''', (new_xp, new_level, new_streak, today.isoformat(), user_id))
        
        conn.commit()
        
        # Check for new badges
        check_and_award_badges(user_id, cursor)
        conn.commit()
        
        return {
            'old_level': stats['level'],
            'new_level': new_level,
            'xp_gained': xp_amount,
            'total_xp': new_xp,
            'level_up': new_level > stats['level']
        }
        
    finally:
        conn.close()

def calculate_level(xp: int) -> int:
    """Calculate level based on XP"""
    for level, threshold in enumerate(LEVEL_THRESHOLDS, 1):
        if xp < threshold:
            return level - 1
    return len(LEVEL_THRESHOLDS)

def check_and_award_badges(user_id: int, cursor):
    """Check and award new badges to user"""
    stats = get_user_stats(user_id)
    
    # Get all badges user doesn't have
    cursor.execute('''
        SELECT b.id, b.name, b.xp_required, b.special_condition
        FROM badges b
        WHERE b.id NOT IN (
            SELECT badge_id FROM user_badges WHERE user_id = ?
        )
    ''', (user_id,))
    
    available_badges = cursor.fetchall()
    new_badges = []
    
    for badge_id, name, xp_required, special_condition in available_badges:
        earned = False
        
        if special_condition == "first_command" and stats['total_commands'] >= 1:
            earned = True
        elif special_condition == "streak_7" and stats['streak_days'] >= 7:
            earned = True
        elif special_condition == "streak_30" and stats['streak_days'] >= 30:
            earned = True
        elif not special_condition and stats['xp_points'] >= xp_required:
            earned = True
        
        if earned:
            cursor.execute('''
                INSERT INTO user_badges (user_id, badge_id)
                VALUES (?, ?)
            ''', (user_id, badge_id))
            new_badges.append(name)
    
    return new_badges

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profil command - Show user profile with XP and badges"""
    user = update.effective_user
    stats = get_user_stats(user.id)
    
    # Get user badges
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.icon, b.name, ub.earned_at
        FROM user_badges ub
        JOIN badges b ON ub.badge_id = b.id
        WHERE ub.user_id = ?
        ORDER BY ub.earned_at DESC
    ''', (user.id,))
    
    badges = cursor.fetchall()
    conn.close()
    
    # Calculate next level info
    current_level = stats['level']
    current_xp = stats['xp_points']
    
    if current_level < len(LEVEL_THRESHOLDS):
        next_level_xp = LEVEL_THRESHOLDS[current_level]
        xp_needed = next_level_xp - current_xp
        progress = (current_xp - LEVEL_THRESHOLDS[current_level - 1]) / (next_level_xp - LEVEL_THRESHOLDS[current_level - 1]) * 100
    else:
        xp_needed = 0
        progress = 100
    
    # Create progress bar
    progress_bar = create_progress_bar(progress)
    
    # Format badges
    badge_text = ""
    if badges:
        badge_text = "\n🏆 **BADGES OBTENUS**\n"
        for icon, name, earned_at in badges[:6]:  # Show max 6 badges
            badge_text += f"{icon} {name}\n"
        if len(badges) > 6:
            badge_text += f"... et {len(badges) - 6} autres badges\n"
    else:
        badge_text = "\n🏆 **BADGES** : Aucun badge obtenu"
    
    profile_text = f"""
╔══════════════════════════╗
║      👤 PROFIL JOUEUR    ║
╚══════════════════════════╝

**{user.first_name or 'Utilisateur'}** (@{user.username or 'N/A'})

🎯 **NIVEAU {current_level}**
⚡ **{current_xp} XP** {'(' + str(xp_needed) + ' XP pour niveau ' + str(current_level + 1) + ')' if xp_needed > 0 else '(MAX LEVEL!)'}

{progress_bar}

📊 **STATISTIQUES**
🔧 **Commandes :** {stats['total_commands']}
🔥 **Série :** {stats['streak_days']} jour(s)
📅 **Dernière activité :** {stats['last_activity']}
{badge_text}

🎮 **Continuez à utiliser le bot pour gagner plus d'XP !**
    """
    
    # Add leaderboard button
    keyboard = [
        [InlineKeyboardButton("🏆 Classement", callback_data="leaderboard")],
        [InlineKeyboardButton("🏅 Tous les badges", callback_data="all_badges")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        profile_text, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /classement command - Show XP leaderboard"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.first_name, u.username, us.xp_points, us.level, us.total_commands
        FROM user_stats us
        JOIN users u ON us.user_id = u.id
        ORDER BY us.xp_points DESC
        LIMIT 10
    ''')
    
    top_users = cursor.fetchall()
    conn.close()
    
    if not top_users:
        await update.message.reply_text("📭 **Aucun utilisateur dans le classement**")
        return
    
    leaderboard_text = """
🏆 **CLASSEMENT XP - TOP 10**

"""
    
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    
    for i, (first_name, username, xp, level, commands) in enumerate(top_users):
        medal = medals[i]
        name = first_name or username or "Utilisateur"
        leaderboard_text += f"{medal} **{name}**\n"
        leaderboard_text += f"   Niveau {level} • {xp} XP • {commands} cmd\n\n"
    
    await update.message.reply_text(leaderboard_text, parse_mode='Markdown')

def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a visual progress bar"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    return f"{'█' * filled}{'░' * empty} {percentage:.1f}%"

# Hook this into command execution
def award_command_xp(user_id: int, command: str):
    """Award XP for using a command"""
    xp_amount = XP_VALUES['command_use']
    
    # Bonus XP for special commands
    if command in ['ai', 'resume', 'idee']:
        xp_amount += XP_VALUES['special_command']
    
    return add_xp(user_id, xp_amount, command)
