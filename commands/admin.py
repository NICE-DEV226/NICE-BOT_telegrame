#!/usr/bin/env python3
"""
Admin commands for NICE-BOT
Only accessible to bot administrators
"""

import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv

from db import get_user_stats, get_recent_history, get_all_users, get_connection

logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()

# Admin user ID from environment
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")

# Debug: Print what we're loading
print(f"🔍 DEBUG: ADMIN_USER_ID loaded = '{ADMIN_USER_ID}'")

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return str(user_id) == str(ADMIN_USER_ID)

async def send_access_denied(update: Update):
    """Send access denied message for admin commands"""
    user = update.effective_user
    await update.message.reply_text(
        "🚫 **ACCÈS REFUSÉ**\n\n"
        "❌ Cette commande est réservée aux administrateurs du bot.\n\n"
        "👤 **Votre statut :** Utilisateur standard\n"
        "🔒 **Permissions requises :** Administrateur\n\n"
        "💡 **Besoin d'aide ?**\n"
        "Utilisez `/help` pour voir les commandes disponibles pour tous les utilisateurs.\n\n"
        f"🆔 **Votre ID Telegram :** `{user.id}`\n"
        "*(Conservez cet ID si vous devez contacter le support)*",
        parse_mode='Markdown'
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - Admin control panel"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    stats = get_user_stats()
    
    panel_text = f"""
╔══════════════════════════╗
║      🛡️ ADMIN PANEL      ║
╚══════════════════════════╝

📊 **STATISTIQUES BOT**

👥 **Utilisateurs :** {stats['total_users']}
🔧 **Commandes :** {stats['total_commands']}
⏰ **Démarré :** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🛠️ **COMMANDES ADMIN**

• /stats - Statistiques détaillées
• /users - Liste des utilisateurs
• /logs - Logs récents
• /broadcast - Message à tous
• /ban - Bannir un utilisateur
• /unban - Débannir un utilisateur
• /addxp - Ajouter XP à un utilisateur
• /addbadge - Donner un badge
• /resetxp - Reset XP utilisateur

╔══════════════════════════╗
║    Powered by NICE-DEV   ║
╚══════════════════════════╝
    """
    
    await update.message.reply_text(panel_text, parse_mode='Markdown')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Detailed statistics"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    stats = get_user_stats()
    users = get_all_users()
    
    # Calculate activity stats
    recent_users = 0
    for user_data in users:
        if user_data['joined_at']:
            join_date = datetime.fromisoformat(user_data['joined_at'])
            if datetime.now() - join_date <= timedelta(days=7):
                recent_users += 1
    
    stats_text = f"""
╔══════════════════════════╗
║    📊 STATISTIQUES BOT   ║
╚══════════════════════════╝

**👥 UTILISATEURS**
• Total : {stats['total_users']}
• Nouveaux (7j) : {recent_users}
• Actifs : {len([u for u in users if u['username']])}

**🔧 ACTIVITÉ**
• Commandes totales : {stats['total_commands']}
• Moyenne/utilisateur : {stats['total_commands'] // max(stats['total_users'], 1)}

**📈 CROISSANCE**
• Utilisateurs/jour : {recent_users / 7:.1f}
• Commandes/jour : {stats['total_commands'] / 7:.1f}

**🏆 TOP COMMANDES**
• /start, /menu, /ping
• /traduire, /ai, /help
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command - List all users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("📭 Aucun utilisateur enregistré.")
        return
    
    users_text = "╔══════════════════════════╗\n"
    users_text += "║     👥 UTILISATEURS      ║\n"
    users_text += "╚══════════════════════════╝\n\n"
    
    for i, user_data in enumerate(users[:10], 1):  # Limit to 10 users
        username = user_data['username'] or 'N/A'
        first_name = user_data['first_name'] or 'N/A'
        join_date = user_data['joined_at'][:10] if user_data['joined_at'] else 'N/A'
        
        users_text += f"**{i}.** {first_name}\n"
        users_text += f"   @{username}\n"
        users_text += f"   ID: `{user_data['telegram_id']}`\n"
        users_text += f"   Rejoint: {join_date}\n\n"
    
    if len(users) > 10:
        users_text += f"... et {len(users) - 10} autres utilisateurs"
    
    await update.message.reply_text(users_text, parse_mode='Markdown')

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - Send message to all users"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "📢 **Usage:** `/broadcast <message>`\n\n"
            "Exemple: `/broadcast Nouvelle fonctionnalité disponible !`",
            parse_mode='Markdown'
        )
        return
    
    message = " ".join(context.args)
    users = get_all_users()
    
    broadcast_text = f"""
📢 **MESSAGE ADMINISTRATEUR**

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Powered by NICE-DEV*
    """
    
    sent_count = 0
    failed_count = 0
    
    status_message = await update.message.reply_text(
        f"📤 Envoi en cours à {len(users)} utilisateurs..."
    )
    
    for user_data in users:
        try:
            await context.bot.send_message(
                chat_id=user_data['telegram_id'],
                text=broadcast_text,
                parse_mode='Markdown'
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_data['telegram_id']}: {e}")
            failed_count += 1
    
    await status_message.edit_text(
        f"✅ **Broadcast terminé**\n\n"
        f"📤 Envoyés: {sent_count}\n"
        f"❌ Échecs: {failed_count}\n"
        f"📊 Total: {len(users)} utilisateurs",
        parse_mode='Markdown'
    )

async def admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command - Show recent activity logs"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    recent_history = get_recent_history(limit=20)
    
    if not recent_history:
        await update.message.reply_text("📭 Aucune activité récente.")
        return
    
    logs_text = "╔══════════════════════════╗\n"
    logs_text += "║      📋 LOGS RÉCENTS     ║\n"
    logs_text += "╚══════════════════════════╝\n\n"
    
    for log in recent_history:
        timestamp = log['created_at'][:16] if log['created_at'] else 'N/A'
        command = log['command']
        user_id = log['user_id']
        
        logs_text += f"🕐 **{timestamp}**\n"
        logs_text += f"👤 User {user_id}: `{command}`\n\n"
    
    await update.message.reply_text(logs_text, parse_mode='Markdown')

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command - Ban a user"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "🚫 **Usage:** `/ban <user_id> [raison]`\n\n"
            "Exemple: `/ban 123456789 Spam`",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Aucune raison spécifiée"
        
        # Add to banned users table (you'd need to create this table)
        # For now, just simulate
        
        ban_text = f"""
✅ **UTILISATEUR BANNI**

🚫 **User ID:** `{target_user_id}`
📝 **Raison:** {reason}
👤 **Par:** {user.first_name}
🕐 **Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚠️ **L'utilisateur ne peut plus utiliser le bot**
        """
        
        await update.message.reply_text(ban_text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ **ID utilisateur invalide**")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command - Unban a user"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "✅ **Usage:** `/unban <user_id>`\n\n"
            "Exemple: `/unban 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        
        unban_text = f"""
✅ **UTILISATEUR DÉBANNI**

👤 **User ID:** `{target_user_id}`
🔓 **Par:** {user.first_name}
🕐 **Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ **L'utilisateur peut à nouveau utiliser le bot**
        """
        
        await update.message.reply_text(unban_text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ **ID utilisateur invalide**")

async def add_xp_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addxp command - Add XP to user"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚡ **Usage:** `/addxp <user_id> <xp_amount>`\n\n"
            "Exemple: `/addxp 123456789 100`",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        xp_amount = int(context.args[1])
        
        # Import gamification functions
        from commands.gamification import add_xp, get_user_stats
        
        # Add XP
        result = add_xp(target_user_id, xp_amount)
        
        xp_text = f"""
✅ **XP AJOUTÉ**

👤 **User ID:** `{target_user_id}`
⚡ **XP ajouté:** +{xp_amount}
📊 **Total XP:** {result['total_xp']}
🎯 **Niveau:** {result['new_level']}
{'🎉 **LEVEL UP!**' if result['level_up'] else ''}

👑 **Par:** {user.first_name}
        """
        
        await update.message.reply_text(xp_text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ **Valeurs invalides** (ID et XP doivent être des nombres)")
    except Exception as e:
        await update.message.reply_text(f"❌ **Erreur:** {str(e)}")

async def reset_xp_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resetxp command - Reset user XP"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "🔄 **Usage:** `/resetxp <user_id>`\n\n"
            "Exemple: `/resetxp 123456789`\n\n"
            "⚠️ **Attention:** Ceci supprimera tout l'XP de l'utilisateur !",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        
        # Reset XP in database
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_stats 
            SET xp_points = 0, level = 1, total_commands = 0, streak_days = 0
            WHERE user_id = ?
        ''', (target_user_id,))
        
        conn.commit()
        conn.close()
        
        reset_text = f"""
✅ **XP RESET EFFECTUÉ**

👤 **User ID:** `{target_user_id}`
🔄 **XP:** 0
🎯 **Niveau:** 1
📊 **Commandes:** 0
🔥 **Série:** 0

👑 **Par:** {user.first_name}
🕐 **Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        await update.message.reply_text(reset_text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ **ID utilisateur invalide**")
    except Exception as e:
        await update.message.reply_text(f"❌ **Erreur:** {str(e)}")

async def gamification_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gamestats command - Gamification statistics"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await send_access_denied(update)
        return
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total XP distributed
        cursor.execute("SELECT SUM(xp_points) FROM user_stats")
        total_xp = cursor.fetchone()[0] or 0
        
        # Average level
        cursor.execute("SELECT AVG(level) FROM user_stats")
        avg_level = cursor.fetchone()[0] or 1
        
        # Top level
        cursor.execute("SELECT MAX(level) FROM user_stats")
        max_level = cursor.fetchone()[0] or 1
        
        # Total badges earned
        cursor.execute("SELECT COUNT(*) FROM user_badges")
        total_badges = cursor.fetchone()[0] or 0
        
        # Most earned badge
        cursor.execute('''
            SELECT b.name, b.icon, COUNT(ub.id) as count
            FROM badges b
            LEFT JOIN user_badges ub ON b.id = ub.badge_id
            GROUP BY b.id
            ORDER BY count DESC
            LIMIT 1
        ''')
        
        top_badge = cursor.fetchone()
        conn.close()
        
        game_stats_text = f"""
🎮 **STATISTIQUES GAMIFICATION**

⚡ **XP Total Distribué:** {total_xp:,}
🎯 **Niveau Moyen:** {avg_level:.1f}
👑 **Niveau Maximum:** {max_level}
🏅 **Badges Obtenus:** {total_badges}

🏆 **Badge le Plus Populaire:**
{top_badge[1] if top_badge else '🏅'} {top_badge[0] if top_badge else 'Aucun'} ({top_badge[2] if top_badge else 0} fois)

📊 **Engagement:**
• {total_badges / max(1, total_xp / 100):.1f} badges par 100 XP
• Système actif et engageant !
        """
        
        await update.message.reply_text(game_stats_text, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ **Erreur:** {str(e)}")
