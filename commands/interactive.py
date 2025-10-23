#!/usr/bin/env python3
"""
Interactive Commands for NICE-BOT
Modern interface with keyboards and buttons
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime

logger = logging.getLogger(__name__)

async def interactive_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /imenu command - Interactive menu with buttons and image"""
    import os
    from pathlib import Path
    
    # Create inline keyboard with categories
    keyboard = [
        [
            InlineKeyboardButton("🧰 Utilitaires", callback_data="cat_utils"),
            InlineKeyboardButton("🤖 IA & Assistant", callback_data="cat_ai")
        ],
        [
            InlineKeyboardButton("🎮 Fun & Divertissement", callback_data="cat_fun"),
            InlineKeyboardButton("📰 Info & Actualités", callback_data="cat_info")
        ],
        [
            InlineKeyboardButton("🎯 Gamification", callback_data="cat_game"),
            InlineKeyboardButton("⏰ Notifications", callback_data="cat_notif")
        ],
        [
            InlineKeyboardButton("🛠️ Développement", callback_data="cat_dev"),
            InlineKeyboardButton("🛡️ Admin", callback_data="cat_admin")
        ],
        [
            InlineKeyboardButton("📞 Support WhatsApp", url="http://bit.ly/473vUob"),
            InlineKeyboardButton("ℹ️ À Propos", callback_data="about_bot")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = """
╔══════════════════════════════════╗
║       🚀 NICE-BOT PRO v2.1       ║
║      MENU INTERACTIF MODERNE     ║
╚══════════════════════════════════╝

🎯 **Choisissez une catégorie :**

Cliquez sur les boutons ci-dessous pour explorer toutes les fonctionnalités de NICE-BOT !

✨ **35+ commandes disponibles**
🤖 **IA intégrée (PrinceTech GPT)**
🎮 **Système de gamification**
⏰ **Notifications et rappels**

💡 **Astuce :** Utilisez /quick pour les actions rapides !
    """
    
    # Try to send with image
    try:
        # Get image path
        image_path = Path(__file__).parent.parent / "assets" / "menu.png"
        
        if image_path.exists():
            # Send photo with caption and buttons
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=menu_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        else:
            # Fallback: send text only if image not found
            await update.message.reply_text(
                menu_text, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending menu with image: {e}")
        # Fallback: send text only
        await update.message.reply_text(
            menu_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def quick_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quick command - Quick action buttons"""
    
    # Create reply keyboard with quick actions
    keyboard = [
        [KeyboardButton("🏓 Ping"), KeyboardButton("👤 Profil")],
        [KeyboardButton("🌤️ Météo Paris"), KeyboardButton("⏰ Rappel 5min Test")],
        [KeyboardButton("🤖 Salut IA"), KeyboardButton("🤣 Meme")],
        [KeyboardButton("🏆 Classement"), KeyboardButton("📋 Menu Interactif")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    quick_text = """
⚡ **ACTIONS RAPIDES**

Utilisez les boutons ci-dessous pour accéder rapidement aux fonctions populaires !

🎯 **Astuce :** Les boutons restent visibles pour un accès ultra-rapide
    """
    
    await update.message.reply_text(
        quick_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "cat_utils":
        keyboard = [
            [InlineKeyboardButton("🌐 Traduire", callback_data="cmd_traduire")],
            [InlineKeyboardButton("🌤️ Météo", callback_data="cmd_meteo")],
            [InlineKeyboardButton("💱 Devises", callback_data="cmd_devise")],
            [InlineKeyboardButton("📱 QR Code", callback_data="cmd_qr")],
            [InlineKeyboardButton("📄 Générer PDF", callback_data="cmd_pdf")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🧰 **UTILITAIRES**\n\nChoisissez l'outil que vous souhaitez utiliser :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_ai":
        keyboard = [
            [InlineKeyboardButton("🤖 Poser Question", callback_data="cmd_ai")],
            [InlineKeyboardButton("📝 Résumer Texte", callback_data="cmd_resume")],
            [InlineKeyboardButton("💡 Générer Idées", callback_data="cmd_idee")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🤖 **INTELLIGENCE ARTIFICIELLE**\n\nQue voulez-vous faire avec l'IA ?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_fun":
        keyboard = [
            [InlineKeyboardButton("😂 Blague", callback_data="cmd_blague")],
            [InlineKeyboardButton("🤣 Meme Reddit", callback_data="cmd_meme")],
            [InlineKeyboardButton("✨ Citation", callback_data="cmd_citation")],
            [InlineKeyboardButton("🎬 Film", callback_data="cmd_film")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎮 **FUN & DIVERTISSEMENT**\n\nUn peu de détente ?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_info":
        keyboard = [
            [InlineKeyboardButton("📰 Actualités", callback_data="cmd_news")],
            [InlineKeyboardButton("📚 Wikipedia", callback_data="cmd_wiki")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📰 **INFO & ACTUALITÉS**\n\nRestez informé !",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_game":
        keyboard = [
            [InlineKeyboardButton("👤 Mon Profil", callback_data="cmd_profil")],
            [InlineKeyboardButton("🏆 Classement", callback_data="cmd_classement")],
            [InlineKeyboardButton("🏅 Tous les Badges", callback_data="cmd_badges")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎮 **GAMIFICATION**\n\nVotre progression et achievements :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_notif":
        keyboard = [
            [InlineKeyboardButton("⏰ Programmer Rappel", callback_data="cmd_rappel")],
            [InlineKeyboardButton("📋 Mes Rappels", callback_data="cmd_rappels")],
            [InlineKeyboardButton("🌦️ Alertes Météo", callback_data="cmd_alertes")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⏰ **NOTIFICATIONS**\n\nGérez vos rappels et alertes :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_dev":
        keyboard = [
            [InlineKeyboardButton("🏓 Test Ping", callback_data="cmd_ping")],
            [InlineKeyboardButton("⏰ Uptime", callback_data="cmd_uptime")],
            [InlineKeyboardButton("📊 Logs", callback_data="cmd_logs")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛠️ **DÉVELOPPEMENT**\n\nOutils de diagnostic :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "cat_admin":
        keyboard = [
            [InlineKeyboardButton("🛡️ Panel Admin", callback_data="cmd_admin")],
            [InlineKeyboardButton("📊 Statistiques", callback_data="cmd_stats")],
            [InlineKeyboardButton("👥 Utilisateurs", callback_data="cmd_users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="cmd_broadcast")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛡️ **ADMINISTRATION**\n\nGestion du bot (Admin uniquement) :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "about_bot":
        keyboard = [
            [InlineKeyboardButton("📞 Support WhatsApp", url="http://bit.ly/473vUob")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        about_text = f"""
🤖 **NICE-BOT PRO v2.0**

🎯 **Assistant Telegram Intelligent**
Développé avec ❤️ par NICE-DEV

🌟 **Fonctionnalités :**
• 20+ commandes utiles
• Interface interactive moderne
• IA intégrée
• Support 24/7

📞 **Support :** WhatsApp disponible
🔄 **Mis à jour :** {datetime.now().strftime('%d/%m/%Y')}

✨ **Merci d'utiliser NICE-BOT !**
        """
        
        await query.edit_message_text(
            about_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "main_menu":
        # Retour au menu principal
        await interactive_menu(query, context)
    
    # Handle direct command callbacks
    elif data.startswith("cmd_"):
        command = data.replace("cmd_", "")
        await query.edit_message_text(
            f"🎯 **Commande sélectionnée :** /{command}\n\n"
            f"Tapez `/{command}` suivi de vos paramètres pour utiliser cette fonction.\n\n"
            f"Exemple : `/{command} votre texte ici`",
            parse_mode='Markdown'
        )

async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hidekeyboard command - Remove reply keyboard"""
    from telegram import ReplyKeyboardRemove
    
    await update.message.reply_text(
        "✅ **Clavier masqué**\n\nUtilisez /quick pour le réafficher ou /imenu pour le menu interactif.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )

async def handle_quick_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quick action button presses"""
    message_text = update.message.text
    
    if message_text == "🏓 Ping":
        from commands.dev import ping
        await ping(update, context)
    elif message_text == "👤 Profil":
        from commands.gamification import profile
        await profile(update, context)
    elif message_text == "🌤️ Météo Paris":
        # Simulate /meteo Paris command
        context.args = ["Paris"]
        from commands.utils import meteo
        await meteo(update, context)
    elif message_text == "⏰ Rappel 5min Test":
        # Simulate /rappel 5min Test command
        context.args = ["5min", "Test"]
        from commands.notifications import set_reminder
        await set_reminder(update, context)
    elif message_text == "🤖 Salut IA":
        # Simulate /ai command
        context.args = ["Salut", "comment", "ça", "va", "?"]
        from commands.ai import ai
        await ai(update, context)
    elif message_text == "🤣 Meme":
        from commands.info import meme
        await meme(update, context)
    elif message_text == "🏆 Classement":
        from commands.gamification import leaderboard
        await leaderboard(update, context)
    elif message_text == "📋 Menu Interactif":
        await interactive_menu(update, context)
