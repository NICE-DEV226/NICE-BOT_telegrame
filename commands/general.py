"""
NICE-BOT - General Commands
/start, /help, /menu, /about commands
"""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from db import add_user, get_user, add_history

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Add user to database
    add_user(
        telegram_id=str(user.id),
        username=user.username,
        first_name=user.first_name
    )
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/start')
    
    welcome_message = f"""
⭓────────────────────────────────⭓
│           ⚡ NICE-BOT ⚡          │
│      𝗩𝗼𝘁𝗿𝗲 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 𝗜𝗻𝘁𝗲𝗹𝗹𝗶𝗴𝗲𝗻𝘁      │
⭓────────────────────────────────⭓

🌟 **Salut {user.first_name or 'utilisateur'} !** 👋

Bienvenue dans l'univers de **NICE-BOT** - le chatbot Telegram le plus polyvalent et intelligent du moment !

✨ **Pourquoi NICE-BOT ?**
• 🚀 **Rapide** - Réponses instantanées 24h/24
• 🧠 **Intelligent** - IA avancée pour tous vos besoins
• 🆓 **Gratuit** - Toutes les fonctionnalités sans limite
• 🔒 **Sécurisé** - Vos données restent privées

🎯 **Ce que je peux faire pour vous :**

🌍 **Utilitaires du quotidien**
Traduction, météo, devises, QR codes, PDF

🤖 **Intelligence Artificielle**
Questions, résumés, génération d'idées créatives

🎮 **Divertissement & Culture**
Blagues, citations, films, actualités, Wikipédia

🛠️ **Outils techniques**
Monitoring, statistiques, logs système

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **Commencez maintenant :**
• Tapez /menu pour découvrir toutes mes capacités
• Tapez /help pour une aide rapide
• Ou essayez directement /ping pour tester !

🚀 **Prêt à explorer ?** Votre aventure commence ici !

*Powered by NICE-DEV*
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/help')
    
    help_text = """
📚 **AIDE RAPIDE - NICE-BOT**

**🧭 Commandes principales :**
• /start - Démarrer le bot
• /menu - Menu complet avec image
• /about - À propos du bot

**🧰 Utilitaires populaires :**
• /traduire <texte> - Traduire du texte
• /meteo <ville> - Météo actuelle
• /devise <montant> <de> <vers> - Convertir devises

**🧠 IA & Assistant :**
• /ai <question> - Poser une question à l'IA
• /resume <texte> - Résumer un texte

**🎮 Fun :**
• /blague - Blague aléatoire
• /citation - Citation inspirante

Pour la liste complète : /imenu (menu interactif)
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command - Redirect to interactive menu"""
    # Import interactive menu function
    from commands.interactive import interactive_menu
    
    # Call interactive menu directly
    await interactive_menu(update, context)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/about')
    
    about_text = """
🤖 **À PROPOS DE NICE-BOT**

**Version :** 1.0.0
**Développé par :** NICE Team
**Hébergement :** Render (Free Tier)
**Base de données :** SQLite
**Framework :** Python + FastAPI + python-telegram-bot

**🎯 Mission :**
Fournir un assistant Telegram gratuit, rapide et polyvalent avec des fonctionnalités utiles pour tous.

**🔧 Fonctionnalités :**
• 20+ commandes utilitaires
• APIs gratuites uniquement
• Disponible 24h/24
• Base de données locale
• Interface moderne

**🌟 APIs utilisées :**
• LibreTranslate (traduction)
• Open-Meteo (météo)
• ExchangeRate.host (devises)
• HuggingFace (IA)
• TMDB (films)
• Wikipedia (encyclopédie)

**📞 Support :**
Pour signaler un bug ou suggérer une amélioration, contactez l'équipe de développement.

**🔒 Confidentialité :**
Vos données sont stockées localement et ne sont jamais partagées avec des tiers.
    """
    
    await update.message.reply_text(about_text, parse_mode='Markdown')
