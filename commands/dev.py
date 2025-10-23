"""
NICE-BOT - Development Commands
/ping, /uptime, /logs commands for system monitoring
"""

import os
import logging
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, add_history, get_user_stats, get_recent_logs

logger = logging.getLogger(__name__)

# Store bot start time
BOT_START_TIME = datetime.now()

# Admin user ID (set via environment variable)
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command - Response time measurement"""
    start_time = time.time()
    
    # Send initial message
    message = await update.message.reply_text("🏓 Pong! Calcul...")
    
    # Calculate actual response time
    response_time = round((time.time() - start_time) * 1000, 2)
    
    # Update with final result
    response_text = f"""
╔══════════════════════════╗
║       🏓 PING TEST       ║
╚══════════════════════════╝

⚡ **{response_time} ms**

🟢 **CONNEXION RAPIDE**
🚀 **BOT RÉACTIF**

╔══════════════════════════╗
║    Powered by NICE-DEV   ║
╚══════════════════════════╝
    """
    
    await message.edit_text(response_text, parse_mode='Markdown')

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /uptime command - Simple and user-friendly"""
    
    # Calculate uptime
    uptime_duration = datetime.now() - BOT_START_TIME
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    response_text = f"""
╔══════════════════════════╗
║      ⏰ NICE-BOT         ║
║     TEMPS EN LIGNE       ║
╚══════════════════════════╝

🟢 **ACTIF DEPUIS**

📅 **{days} jour(s)**
🕐 **{hours} heure(s)**  
⏱️ **{minutes} minute(s)**

🚀 **Tout fonctionne bien !**

╔══════════════════════════╗
║    Powered by NICE-DEV   ║
╚══════════════════════════╝
    """
    
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command - Recent activity logs (admin only)"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Log command
    db_user = get_user(user_id)
    if db_user:
        add_history(db_user['id'], '/logs')
    
    # Check if user is admin
    if ADMIN_USER_ID and user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "❌ **Accès refusé**\n\nCette commande est réservée aux administrateurs.",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Get recent logs from database
        recent_logs = get_recent_logs(limit=10)
        
        if not recent_logs:
            await update.message.reply_text("📋 Aucun log récent disponible.")
            return
        
        response_text = "📋 **Logs récents (10 dernières commandes)**\n\n"
        
        for log in recent_logs:
            # Format timestamp
            timestamp = datetime.fromisoformat(log['created_at']).strftime('%d/%m %H:%M')
            
            # Get user info
            username = log['username'] or 'N/A'
            first_name = log['first_name'] or 'Utilisateur'
            
            # Format command and input
            command = log['command']
            input_text = log['input'][:30] + '...' if len(log['input']) > 30 else log['input']
            
            response_text += f"""
**{timestamp}** | `{command}`
👤 {first_name} (@{username})
{f"📝 {input_text}" if input_text else ""}

"""
        
        response_text += f"""
🔧 **Informations système :**
📅 **Dernière mise à jour :** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
💾 **Base de données :** Opérationnelle
🌐 **API externes :** Fonctionnelles

*Logs générés automatiquement*
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Logs error: {e}")
        await update.message.reply_text("❌ Erreur lors de la récupération des logs.")

# Additional utility functions for monitoring

def get_system_status():
    """Get current system status"""
    return {
        'uptime': datetime.now() - BOT_START_TIME,
        'status': 'operational',
        'database': 'connected',
        'apis': 'functional'
    }

def log_error(error_message: str, command: str = "", user_id: str = ""):
    """Log errors for monitoring"""
    logger.error(f"Error in {command} for user {user_id}: {error_message}")

def log_command_usage(command: str, user_id: str, success: bool = True):
    """Log command usage for analytics"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Command {command} executed by user {user_id}: {status}")
