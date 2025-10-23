"""
NICE-BOT - Telegram Bot Configuration
Main bot setup and command registration
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import command modules
from commands.general import start, help_command, menu, about
from commands.utils import traduire, meteo, devise, qr, pdf
from commands.ai import ai, resume, idee
from commands.info import citation, blague, film, news, wiki, meme
from commands.dev import ping, uptime, logs
from commands.admin import (admin_panel, admin_stats, admin_users, admin_broadcast, admin_logs,
                            ban_user, unban_user, add_xp_admin, reset_xp_admin, gamification_stats)
from commands.interactive import interactive_menu, quick_actions, handle_callback, remove_keyboard, handle_quick_buttons
from commands.notifications import set_reminder, list_reminders, weather_alerts
from commands.gamification import profile, leaderboard
from commands.chatbot import chatbot_command, handle_chatbot_message
from commands.downloader import (tiktok_download, facebook_download, instagram_download, 
                                 twitter_download, pinterest_download, apk_download)
from commands.group_management import (welcome_group, setup_group, invite_link, 
                                       group_info, bot_permissions)
from commands.channel_management import (list_groups, leave_group, broadcast_to_groups, 
                                         group_stats_admin)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Debug: Check if .env is loaded
logger.info(f"DEBUG bot.py: BOT_TOKEN = {os.getenv('BOT_TOKEN', 'NOT_FOUND')[:20]}...")
logger.info(f"DEBUG bot.py: ADMIN_USER_ID = '{os.getenv('ADMIN_USER_ID', 'NOT_FOUND')}'")

def setup_bot() -> Application:
    """Setup and configure the Telegram bot"""
    
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")
    
    # Create application with optimized settings
    application = (
        Application.builder()
        .token(bot_token)
        .concurrent_updates(True)           # Enable concurrent processing
        .pool_timeout(30.0)                 # Connection pool timeout
        .connection_pool_size(8)            # Smaller pool for free tier
        .read_timeout(20.0)                 # Faster read timeout
        .write_timeout(20.0)                # Faster write timeout
        .connect_timeout(10.0)              # Faster connection timeout
        .get_updates_pool_timeout(5.0)      # Faster polling timeout
        .build()
    )
    
    # Register command handlers
    
    # General commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("about", about))
    
    # Utility commands
    application.add_handler(CommandHandler("traduire", traduire))
    application.add_handler(CommandHandler("meteo", meteo))
    application.add_handler(CommandHandler("devise", devise))
    application.add_handler(CommandHandler("qr", qr))
    application.add_handler(CommandHandler("pdf", pdf))
    
    # AI commands
    application.add_handler(CommandHandler("ai", ai))
    application.add_handler(CommandHandler("resume", resume))
    application.add_handler(CommandHandler("idee", idee))
    
    # Info/Fun commands
    application.add_handler(CommandHandler("citation", citation))
    application.add_handler(CommandHandler("blague", blague))
    application.add_handler(CommandHandler("film", film))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("wiki", wiki))
    application.add_handler(CommandHandler("meme", meme))
    
    # Dev commands
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("logs", logs))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CommandHandler("users", admin_users))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("addxp", add_xp_admin))
    application.add_handler(CommandHandler("resetxp", reset_xp_admin))
    application.add_handler(CommandHandler("gamestats", gamification_stats))
    
    # Interactive commands
    application.add_handler(CommandHandler("imenu", interactive_menu))
    application.add_handler(CommandHandler("quick", quick_actions))
    application.add_handler(CommandHandler("hidekeyboard", remove_keyboard))
    
    # Notification commands
    application.add_handler(CommandHandler("rappel", set_reminder))
    application.add_handler(CommandHandler("rappels", list_reminders))
    application.add_handler(CommandHandler("alertes", weather_alerts))
    
    # Gamification commands
    application.add_handler(CommandHandler("profil", profile))
    application.add_handler(CommandHandler("classement", leaderboard))
    
    # Downloader commands
    application.add_handler(CommandHandler("tiktok", tiktok_download))
    application.add_handler(CommandHandler("facebook", facebook_download))
    application.add_handler(CommandHandler("instagram", instagram_download))
    application.add_handler(CommandHandler("twitter", twitter_download))
    application.add_handler(CommandHandler("pinterest", pinterest_download))
    application.add_handler(CommandHandler("apk", apk_download))
    
    # Chatbot command
    application.add_handler(CommandHandler("chatbot", chatbot_command))
    
    # Group management commands
    application.add_handler(CommandHandler("setup", setup_group))
    application.add_handler(CommandHandler("invite", invite_link))
    application.add_handler(CommandHandler("groupinfo", group_info))
    application.add_handler(CommandHandler("permissions", bot_permissions))
    
    # Admin group/channel management commands
    application.add_handler(CommandHandler("listgroups", list_groups))
    application.add_handler(CommandHandler("leavegroup", leave_group))
    application.add_handler(CommandHandler("broadcastgroups", broadcast_to_groups))
    application.add_handler(CommandHandler("groupstats", group_stats_admin))
    
    # Welcome message when bot is added to group
    from telegram.ext import ChatMemberHandler
    async def track_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track when bot is added to a group"""
        result = update.my_chat_member
        if result.new_chat_member.status == "member":
            await welcome_group(update, context)
    
    application.add_handler(ChatMemberHandler(track_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # Callback query handler for inline keyboards
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Handle chatbot messages (mentions and replies) - BEFORE quick buttons
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_chatbot_message
    ))
    
    # Handle quick action buttons
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_quick_buttons
    ))
    
    # Handle unknown commands
    async def unknown_command(update, context):
        """Handle unknown commands"""
        await update.message.reply_text(
            "❌ Commande inconnue. Utilisez /imenu pour le menu interactif ou /help pour l'aide."
        )
    
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    logger.info("Bot handlers registered successfully")
    return application

async def setup_menu_button(application: Application):
    """Setup the Telegram menu button with bot commands"""
    from telegram import MenuButtonCommands, BotCommand
    
    try:
        # Define bot commands with descriptions
        commands = [
            BotCommand("start", "🚀 Démarrer le bot"),
            BotCommand("imenu", "🎯 Menu interactif moderne"),
            BotCommand("quick", "⚡ Actions rapides"),
            BotCommand("menu", "📋 Menu (redirige vers imenu)"),
            BotCommand("profil", "👤 Votre profil XP et badges"),
            BotCommand("classement", "🏆 Classement des joueurs"),
            BotCommand("chatbot", "🤖 Activer/désactiver chatbot IA"),
            BotCommand("rappel", "⏰ Programmer un rappel"),
            BotCommand("rappels", "📋 Voir mes rappels"),
            BotCommand("alertes", "🌦️ Alertes météo"),
            BotCommand("traduire", "🌐 Traduire du texte"),
            BotCommand("meteo", "🌤️ Météo d'une ville"),
            BotCommand("devise", "💱 Convertir devises"),
            BotCommand("ai", "🤖 Poser question à l'IA"),
            BotCommand("resume", "📝 Résumer un texte"),
            BotCommand("idee", "💡 Générer des idées"),
            BotCommand("blague", "😂 Blague aléatoire"),
            BotCommand("citation", "✨ Citation inspirante"),
            BotCommand("meme", "🤣 Meme aléatoire Reddit"),
            BotCommand("film", "🎬 Rechercher un film"),
            BotCommand("news", "📰 Actualités"),
            BotCommand("wiki", "📚 Recherche Wikipedia"),
            BotCommand("qr", "📱 Générer QR code"),
            BotCommand("pdf", "📄 Générer PDF"),
            BotCommand("tiktok", "📱 Télécharger TikTok"),
            BotCommand("facebook", "📘 Télécharger Facebook"),
            BotCommand("instagram", "📸 Télécharger Instagram"),
            BotCommand("twitter", "🐦 Télécharger Twitter"),
            BotCommand("pinterest", "📌 Télécharger Pinterest"),
            BotCommand("apk", "📦 Télécharger APK"),
            BotCommand("setup", "⚙️ Configuration groupe"),
            BotCommand("invite", "📨 Inviter le bot"),
            BotCommand("groupinfo", "📊 Infos du groupe"),
            BotCommand("permissions", "🔒 Permissions bot"),
            BotCommand("ping", "🏓 Test de connexion"),
            BotCommand("uptime", "⏰ Temps en ligne"),
            BotCommand("hidekeyboard", "🙈 Masquer clavier"),
            BotCommand("help", "❓ Aide rapide"),
            BotCommand("about", "ℹ️ À propos du bot"),
            BotCommand("admin", "🛡️ Panel administrateur"),
            BotCommand("stats", "📊 Statistiques (admin)"),
            BotCommand("users", "👥 Liste utilisateurs (admin)"),
            BotCommand("broadcast", "📢 Message à tous (admin)"),
            BotCommand("ban", "🚫 Bannir utilisateur (admin)"),
            BotCommand("unban", "✅ Débannir utilisateur (admin)"),
            BotCommand("addxp", "⚡ Ajouter XP (admin)"),
            BotCommand("resetxp", "🔄 Reset XP (admin)"),
            BotCommand("gamestats", "🎮 Stats gamification (admin)"),
            BotCommand("listgroups", "📋 Liste groupes (admin)"),
            BotCommand("leavegroup", "🚪 Quitter groupe (admin)"),
            BotCommand("broadcastgroups", "📢 Broadcast groupes (admin)"),
            BotCommand("groupstats", "📊 Stats groupes (admin)")
        ]
        
        # Set bot commands
        await application.bot.set_my_commands(commands)
        
        # Set menu button to show commands
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonCommands()
        )
        
        logger.info("Menu button and commands configured successfully")
    except Exception as e:
        logger.error(f"Failed to setup menu button: {e}")
