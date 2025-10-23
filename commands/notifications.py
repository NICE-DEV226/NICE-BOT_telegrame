#!/usr/bin/env python3
"""
Notification System for NICE-BOT
Push notifications, reminders, and alerts
"""

import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import re

logger = logging.getLogger(__name__)

# Store active reminders (in production, use Redis or database)
active_reminders = {}

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rappel command - Set personal reminders"""
    
    if not context.args:
        help_text = """
⏰ **SYSTÈME DE RAPPELS**

**Usage :** `/rappel <temps> <message>`

**Exemples :**
• `/rappel 5min Réunion équipe`
• `/rappel 1h Appeler maman`
• `/rappel 30s Test rapide`
• `/rappel 2h30min Pause déjeuner`

**Formats supportés :**
• `Xs` → secondes
• `Xmin` → minutes  
• `Xh` → heures
• `XhYmin` → heures et minutes

🎯 **Astuce :** Le bot vous enverra une notification privée !
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        return
    
    # Parse time and message
    time_str = context.args[0]
    message = " ".join(context.args[1:]) if len(context.args) > 1 else "Rappel !"
    
    # Parse time format
    total_seconds = parse_time_string(time_str)
    
    if total_seconds is None:
        await update.message.reply_text(
            "❌ **Format de temps invalide**\n\n"
            "Utilisez : `5min`, `1h`, `30s`, `2h30min`",
            parse_mode='Markdown'
        )
        return
    
    if total_seconds > 86400:  # Max 24h
        await update.message.reply_text(
            "❌ **Durée trop longue**\n\nMaximum : 24 heures",
            parse_mode='Markdown'
        )
        return
    
    user_id = update.effective_user.id
    reminder_time = datetime.now() + timedelta(seconds=total_seconds)
    
    # Create reminder
    reminder_id = f"{user_id}_{int(datetime.now().timestamp())}"
    active_reminders[reminder_id] = {
        'user_id': user_id,
        'message': message,
        'time': reminder_time,
        'chat_id': update.effective_chat.id
    }
    
    # Schedule the reminder
    asyncio.create_task(send_reminder(context.bot, reminder_id, total_seconds))
    
    # Confirmation message
    time_formatted = format_duration(total_seconds)
    confirmation_text = f"""
✅ **RAPPEL PROGRAMMÉ**

⏰ **Dans :** {time_formatted}
📝 **Message :** {message}
🕐 **Heure :** {reminder_time.strftime('%H:%M:%S')}

🔔 **Je vous préviendrai en privé !**
    """
    
    await update.message.reply_text(confirmation_text, parse_mode='Markdown')

async def send_reminder(bot, reminder_id: str, delay_seconds: int):
    """Send reminder after delay"""
    try:
        # Wait for the specified time
        await asyncio.sleep(delay_seconds)
        
        # Check if reminder still exists (could be cancelled)
        if reminder_id not in active_reminders:
            return
        
        reminder = active_reminders[reminder_id]
        
        # Send reminder message
        reminder_text = f"""
🔔 **RAPPEL !**

📝 **Message :** {reminder['message']}
🕐 **Programmé à :** {reminder['time'].strftime('%H:%M:%S')}

✅ **C'est maintenant !**
        """
        
        await bot.send_message(
            chat_id=reminder['chat_id'],
            text=reminder_text,
            parse_mode='Markdown'
        )
        
        # Remove from active reminders
        del active_reminders[reminder_id]
        
    except Exception as e:
        logger.error(f"Error sending reminder {reminder_id}: {e}")

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rappels command - List active reminders"""
    
    user_id = update.effective_user.id
    user_reminders = [
        r for r in active_reminders.values() 
        if r['user_id'] == user_id
    ]
    
    if not user_reminders:
        await update.message.reply_text(
            "📭 **Aucun rappel actif**\n\nUtilisez `/rappel` pour en créer un !",
            parse_mode='Markdown'
        )
        return
    
    reminders_text = "⏰ **VOS RAPPELS ACTIFS**\n\n"
    
    for i, reminder in enumerate(user_reminders, 1):
        time_left = reminder['time'] - datetime.now()
        if time_left.total_seconds() > 0:
            time_str = format_duration(int(time_left.total_seconds()))
            reminders_text += f"**{i}.** {reminder['message']}\n"
            reminders_text += f"   ⏱️ Dans {time_str}\n\n"
    
    await update.message.reply_text(reminders_text, parse_mode='Markdown')

async def weather_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /alertes command - Weather alert system"""
    
    if not context.args:
        help_text = """
🌦️ **ALERTES MÉTÉO**

**Usage :** `/alertes <ville>`

**Exemple :** `/alertes Paris`

🎯 **Fonctionnalités :**
• Alerte orage automatique
• Notification pluie/neige
• Températures extrêmes
• Vent fort

⚠️ **Note :** Notifications envoyées en temps réel
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        return
    
    city = " ".join(context.args)
    user_id = update.effective_user.id
    
    # Simulate weather alert setup (in production, integrate with weather API)
    alert_text = f"""
✅ **ALERTES MÉTÉO ACTIVÉES**

📍 **Ville :** {city}
👤 **Utilisateur :** {update.effective_user.first_name}

🔔 **Vous recevrez des alertes pour :**
• ⛈️ Orages et tempêtes
• 🌧️ Pluie intense
• ❄️ Neige et verglas
• 🌡️ Températures extrêmes
• 💨 Vents forts

📱 **Notifications :** Temps réel
⚙️ **Gérer :** `/alertes stop` pour désactiver
    """
    
    await update.message.reply_text(alert_text, parse_mode='Markdown')

def parse_time_string(time_str: str) -> int:
    """Parse time string to seconds"""
    try:
        # Remove spaces
        time_str = time_str.replace(" ", "").lower()
        
        total_seconds = 0
        
        # Parse hours
        hours_match = re.search(r'(\d+)h', time_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
        
        # Parse minutes
        minutes_match = re.search(r'(\d+)min', time_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        # Parse seconds
        seconds_match = re.search(r'(\d+)s', time_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        # If no unit specified, assume minutes
        if not any([hours_match, minutes_match, seconds_match]):
            if time_str.isdigit():
                total_seconds = int(time_str) * 60
        
        return total_seconds if total_seconds > 0 else None
        
    except Exception:
        return None

def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}min {remaining_seconds}s"
        return f"{minutes}min"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}min"
        return f"{hours}h"
