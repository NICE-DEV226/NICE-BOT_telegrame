#!/usr/bin/env python3
"""
NICE-BOT - Group Management Commands
Professional group and channel integration features
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from db import get_user, add_history

logger = logging.getLogger(__name__)

# Data file for group settings
GROUP_DATA_FILE = Path(__file__).parent.parent / "data" / "group_settings.json"

def load_group_settings():
    """Load group settings from file"""
    try:
        GROUP_DATA_FILE.parent.mkdir(exist_ok=True)
        if GROUP_DATA_FILE.exists():
            with open(GROUP_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'groups': {}, 'channels': {}}
    except Exception as e:
        logger.error(f"Error loading group settings: {e}")
        return {'groups': {}, 'channels': {}}

def save_group_settings(data):
    """Save group settings to file"""
    try:
        GROUP_DATA_FILE.parent.mkdir(exist_ok=True)
        with open(GROUP_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving group settings: {e}")

async def welcome_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when bot is added to a group"""
    chat = update.effective_chat
    
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # Save group info
        settings = load_group_settings()
        chat_id_str = str(chat.id)
        
        settings['groups'][chat_id_str] = {
            'name': chat.title,
            'type': chat.type,
            'added_at': datetime.now().isoformat(),
            'member_count': await context.bot.get_chat_member_count(chat.id)
        }
        save_group_settings(settings)
        
        # Create welcome keyboard
        keyboard = [
            [
                InlineKeyboardButton("📋 Menu Complet", callback_data="group_menu"),
                InlineKeyboardButton("⚙️ Configuration", callback_data="group_config")
            ],
            [
                InlineKeyboardButton("🤖 Activer Chatbot", callback_data="chatbot_on"),
                InlineKeyboardButton("📥 Téléchargements", callback_data="downloads_info")
            ],
            [
                InlineKeyboardButton("❓ Aide", callback_data="group_help"),
                InlineKeyboardButton("📊 Statistiques", callback_data="group_stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
╔═══════════════════════════════════╗
║     🎉 BIENVENUE DANS NICE-BOT    ║
╚═══════════════════════════════════╝

Merci d'avoir ajouté **NICE-BOT** à votre groupe !

**🎯 Groupe :** {chat.title}
**👥 Membres :** {await context.bot.get_chat_member_count(chat.id)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✨ FONCTIONNALITÉS PRINCIPALES :**

🤖 **Chatbot IA Intelligent**
   • Activez avec `/chatbot on`
   • Réponses automatiques aux mentions
   • Mémoire de conversation

📥 **Téléchargements**
   • TikTok, Instagram, Facebook
   • Twitter, Pinterest
   • APK (applications)

🌐 **Utilitaires**
   • Traduction (12 langues)
   • Météo en temps réel
   • Conversion de devises (30+)
   • QR codes, PDF

🎮 **Divertissement**
   • IA conversationnelle
   • Blagues, citations, memes
   • Recherche films et actualités

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🚀 DÉMARRAGE RAPIDE :**

1️⃣ Utilisez `/menu` pour le menu interactif
2️⃣ Tapez `/help` pour l'aide complète
3️⃣ Configurez avec les boutons ci-dessous

**💡 Astuce :** Les admins peuvent activer le chatbot IA pour des réponses automatiques !

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **NICE-BOT** - Votre assistant intelligent
        """
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setup command - Group configuration"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/setup', '')
    
    # Check if it's a group
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await update.message.reply_text(
            "⚠️ Cette commande est réservée aux groupes.",
            parse_mode='Markdown'
        )
        return
    
    # Check if user is admin
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        is_admin = member.status in ['creator', 'administrator']
    except:
        is_admin = False
    
    if not is_admin:
        await update.message.reply_text(
            "❌ **Accès refusé**\n\n"
            "Seuls les administrateurs peuvent configurer le bot.",
            parse_mode='Markdown'
        )
        return
    
    # Create setup keyboard
    keyboard = [
        [
            InlineKeyboardButton("🤖 Chatbot IA", callback_data="setup_chatbot"),
            InlineKeyboardButton("📥 Téléchargements", callback_data="setup_downloads")
        ],
        [
            InlineKeyboardButton("🎮 Gamification", callback_data="setup_game"),
            InlineKeyboardButton("⏰ Notifications", callback_data="setup_notif")
        ],
        [
            InlineKeyboardButton("🌐 Langue", callback_data="setup_lang"),
            InlineKeyboardButton("🔒 Permissions", callback_data="setup_perms")
        ],
        [
            InlineKeyboardButton("📊 Voir Config", callback_data="view_config"),
            InlineKeyboardButton("🔄 Réinitialiser", callback_data="reset_config")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    setup_text = f"""
╔═══════════════════════════════════╗
║    ⚙️ CONFIGURATION DU GROUPE     ║
╚═══════════════════════════════════╝

**Groupe :** {chat.title}
**Admin :** {user.first_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎯 MODULES DISPONIBLES :**

🤖 **Chatbot IA**
   Configure les réponses automatiques

📥 **Téléchargements**
   Active/désactive les téléchargements

🎮 **Gamification**
   Système XP et badges pour le groupe

⏰ **Notifications**
   Rappels et alertes pour les membres

🌐 **Langue**
   Choisir la langue du bot

🔒 **Permissions**
   Gérer qui peut utiliser quelles commandes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Cliquez sur les boutons pour configurer**
    """
    
    await update.message.reply_text(
        setup_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /invite command - Generate invite link"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/invite', '')
    
    bot_username = context.bot.username
    
    # Create invite keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Ajouter à un Groupe",
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Ajouter à un Canal",
                url=f"https://t.me/{bot_username}?startchannel=true"
            )
        ],
        [
            InlineKeyboardButton(
                "💬 Discuter en Privé",
                url=f"https://t.me/{bot_username}?start=hello"
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Documentation",
                url="https://github.com/yourusername/nice-bot"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    invite_text = f"""
╔═══════════════════════════════════╗
║    📨 INVITER NICE-BOT           ║
╚═══════════════════════════════════╝

**Partagez NICE-BOT avec vos amis !**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎯 MÉTHODES D'INVITATION :**

**1️⃣ Lien Direct :**
`https://t.me/{bot_username}`

**2️⃣ Pour Groupes :**
`https://t.me/{bot_username}?startgroup=true`

**3️⃣ Pour Canaux :**
`https://t.me/{bot_username}?startchannel=true`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✨ FONCTIONNALITÉS :**

• 🤖 Chatbot IA intelligent
• 📥 Téléchargements (TikTok, Insta, etc.)
• 🌐 Traduction 12 langues
• 🎮 Système de gamification
• 💱 Conversion 30+ devises
• 📊 Statistiques et analytics
• ⏰ Rappels et notifications

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Astuce :** Cliquez sur les boutons ci-dessous pour une invitation rapide !

**🆓 100% Gratuit | 🔒 Sécurisé | ⚡ Rapide**
    """
    
    await update.message.reply_text(
        invite_text,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def group_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /groupinfo command - Show group information"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/groupinfo', '')
    
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await update.message.reply_text(
            "⚠️ Cette commande est réservée aux groupes.",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Get group info
        member_count = await context.bot.get_chat_member_count(chat.id)
        
        # Get admin count
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_count = len(admins)
        
        # Load settings
        settings = load_group_settings()
        chat_id_str = str(chat.id)
        group_data = settings.get('groups', {}).get(chat_id_str, {})
        
        # Check features status
        from commands.chatbot import is_chatbot_enabled
        chatbot_status = "✅ Activé" if is_chatbot_enabled(chat.id) else "❌ Désactivé"
        
        info_text = f"""
╔═══════════════════════════════════╗
║    📊 INFORMATIONS DU GROUPE     ║
╚═══════════════════════════════════╝

**📝 Nom :** {chat.title}
**🆔 ID :** `{chat.id}`
**👥 Membres :** {member_count}
**👮 Admins :** {admin_count}
**📅 Ajouté le :** {group_data.get('added_at', 'N/A')[:10] if group_data.get('added_at') else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚙️ FONCTIONNALITÉS ACTIVES :**

🤖 **Chatbot IA :** {chatbot_status}
📥 **Téléchargements :** ✅ Disponible
🎮 **Gamification :** ✅ Disponible
🌐 **Traduction :** ✅ Disponible
💱 **Conversion :** ✅ Disponible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🎯 COMMANDES UTILES :**

• `/setup` - Configuration du groupe
• `/chatbot on` - Activer le chatbot
• `/menu` - Menu interactif
• `/help` - Aide complète

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **NICE-BOT** - Votre assistant de groupe
        """
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error getting group info: {e}")
        await update.message.reply_text(
            "❌ Erreur lors de la récupération des informations.",
            parse_mode='Markdown'
        )

async def bot_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /permissions command - Check bot permissions"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/permissions', '')
    
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await update.message.reply_text(
            "⚠️ Cette commande est réservée aux groupes.",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Get bot member info
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        
        # Check permissions
        perms = bot_member.privileges if hasattr(bot_member, 'privileges') else None
        
        if bot_member.status == 'administrator' and perms:
            perms_text = f"""
╔═══════════════════════════════════╗
║    🔒 PERMISSIONS DU BOT         ║
╚═══════════════════════════════════╝

**Statut :** 🛡️ Administrateur

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✅ PERMISSIONS ACCORDÉES :**

{'✅' if perms.can_delete_messages else '❌'} Supprimer messages
{'✅' if perms.can_restrict_members else '❌'} Restreindre membres
{'✅' if perms.can_promote_members else '❌'} Promouvoir membres
{'✅' if perms.can_change_info else '❌'} Modifier infos groupe
{'✅' if perms.can_invite_users else '❌'} Inviter utilisateurs
{'✅' if perms.can_pin_messages else '❌'} Épingler messages
{'✅' if perms.can_manage_chat else '❌'} Gérer le chat

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 RECOMMANDATIONS :**

Pour un fonctionnement optimal, accordez au bot les permissions suivantes :
• ✅ Supprimer messages (modération)
• ✅ Épingler messages (annonces)
• ✅ Inviter utilisateurs (croissance)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **NICE-BOT** fonctionne parfaitement !
            """
        else:
            perms_text = f"""
╔═══════════════════════════════════╗
║    🔒 PERMISSIONS DU BOT         ║
╚═══════════════════════════════════╝

**Statut :** 👤 Membre Standard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚠️ PERMISSIONS LIMITÉES**

Le bot fonctionne en mode limité.

**💡 POUR DÉBLOQUER TOUTES LES FONCTIONNALITÉS :**

1️⃣ Allez dans les paramètres du groupe
2️⃣ Cliquez sur "Administrateurs"
3️⃣ Ajoutez le bot comme administrateur
4️⃣ Accordez les permissions nécessaires

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✨ FONCTIONNALITÉS DISPONIBLES :**

✅ Commandes de base
✅ Chatbot IA
✅ Téléchargements
✅ Traduction
✅ Utilitaires

**🔒 FONCTIONNALITÉS RESTREINTES :**

❌ Modération automatique
❌ Gestion des membres
❌ Épinglage de messages
            """
        
        await update.message.reply_text(perms_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error checking permissions: {e}")
        await update.message.reply_text(
            "❌ Erreur lors de la vérification des permissions.",
            parse_mode='Markdown'
        )
