#!/usr/bin/env python3
"""
Chatbot Command for NICE-BOT
AI chatbot that can be enabled/disabled in groups by admins
"""

import os
import json
import logging
import aiohttp
import asyncio
import random
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, add_history

logger = logging.getLogger(__name__)

# Data file for chatbot settings
CHATBOT_DATA_FILE = Path(__file__).parent.parent / "data" / "chatbot_settings.json"

# In-memory storage for chat history
chat_memory = {
    'messages': {},  # Stores last 20 messages per user
    'user_info': {}  # Stores user information
}

def load_chatbot_settings():
    """Load chatbot settings from file"""
    try:
        CHATBOT_DATA_FILE.parent.mkdir(exist_ok=True)
        if CHATBOT_DATA_FILE.exists():
            with open(CHATBOT_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'enabled_chats': {}}
    except Exception as e:
        logger.error(f"Error loading chatbot settings: {e}")
        return {'enabled_chats': {}}

def save_chatbot_settings(data):
    """Save chatbot settings to file"""
    try:
        CHATBOT_DATA_FILE.parent.mkdir(exist_ok=True)
        with open(CHATBOT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving chatbot settings: {e}")

def is_chatbot_enabled(chat_id):
    """Check if chatbot is enabled for a chat"""
    settings = load_chatbot_settings()
    return str(chat_id) in settings.get('enabled_chats', {})

async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin in the group"""
    user = update.effective_user
    chat = update.effective_chat
    
    # In private chats, user is always admin
    if chat.type == 'private':
        return True
    
    # Check if user is admin in group
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def chatbot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chatbot command - Enable/disable chatbot in groups and private chats"""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/chatbot', ' '.join(context.args))
    
    # Check if user is admin (in groups) or if it's a private chat
    is_admin = await is_user_admin(update, context)
    is_private = chat.type == 'private'
    
    if not context.args:
        status = "✅ Activé" if is_chatbot_enabled(chat.id) else "❌ Désactivé"
        chat_type = "conversation privée" if is_private else "groupe"
        
        await update.message.reply_text(
            f"🤖 **CHATBOT IA**\n\n"
            f"**Type de chat :** {chat_type}\n"
            f"**Statut actuel :** {status}\n\n"
            f"**Usage :**\n"
            f"• `/chatbot on` - Activer le chatbot\n"
            f"• `/chatbot off` - Désactiver le chatbot\n\n"
            f"**Fonctionnement :**\n"
            f"{'• En privé : Tous les messages sont traités\n' if is_private else ''}"
            f"{'• En groupe : Mentionnez le bot ou répondez à ses messages\n' if not is_private else ''}"
            f"• Le bot répondra automatiquement avec l'IA\n\n"
            f"{'⚠️ En groupe, seuls les admins peuvent activer/désactiver' if not is_private and not is_admin else '✅ Vous pouvez gérer le chatbot'}",
            parse_mode='Markdown'
        )
        return
    
    command = context.args[0].lower()
    
    # Check admin permission for on/off commands (only in groups)
    if command in ['on', 'off'] and not is_private and not is_admin:
        await update.message.reply_text(
            "❌ **Accès refusé**\n\n"
            "Seuls les administrateurs du groupe peuvent activer/désactiver le chatbot.",
            parse_mode='Markdown'
        )
        return
    
    settings = load_chatbot_settings()
    chat_id_str = str(chat.id)
    
    if command == 'on':
        if is_chatbot_enabled(chat.id):
            await update.message.reply_text(
                "ℹ️ Le chatbot est déjà activé pour ce chat.",
                parse_mode='Markdown'
            )
            return
        
        settings['enabled_chats'][chat_id_str] = {
            'enabled_at': datetime.now().isoformat(),
            'enabled_by': user.id,
            'chat_name': chat.title or chat.first_name or 'Unknown'
        }
        save_chatbot_settings(settings)
        
        await update.message.reply_text(
            "✅ **Chatbot activé !**\n\n"
            "Le bot répondra maintenant aux mentions et aux réponses.\n\n"
            "💡 **Astuce :** Mentionnez-moi ou répondez à mes messages pour discuter !",
            parse_mode='Markdown'
        )
        logger.info(f"Chatbot enabled for chat {chat_id_str} by user {user.id}")
    
    elif command == 'off':
        if not is_chatbot_enabled(chat.id):
            await update.message.reply_text(
                "ℹ️ Le chatbot est déjà désactivé pour ce chat.",
                parse_mode='Markdown'
            )
            return
        
        if chat_id_str in settings['enabled_chats']:
            del settings['enabled_chats'][chat_id_str]
        save_chatbot_settings(settings)
        
        await update.message.reply_text(
            "❌ **Chatbot désactivé**\n\n"
            "Le bot ne répondra plus automatiquement aux messages.",
            parse_mode='Markdown'
        )
        logger.info(f"Chatbot disabled for chat {chat_id_str} by user {user.id}")
    
    else:
        await update.message.reply_text(
            "❌ Commande invalide. Utilisez `/chatbot` pour voir l'aide.",
            parse_mode='Markdown'
        )

async def handle_chatbot_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages for chatbot auto-response"""
    if not update.message or not update.message.text:
        return
    
    chat = update.effective_chat
    user = update.effective_user
    message_text = update.message.text
    
    # Check if chatbot is enabled for this chat
    if not is_chatbot_enabled(chat.id):
        return
    
    # In private chats, respond to ALL messages
    is_private = chat.type == 'private'
    
    if is_private:
        # In private chat, process all messages
        cleaned_message = message_text.strip()
    else:
        # In groups, only respond to mentions or replies
        bot_username = context.bot.username
        is_mentioned = f"@{bot_username}" in message_text
        is_reply_to_bot = False
        
        if update.message.reply_to_message:
            is_reply_to_bot = update.message.reply_to_message.from_user.id == context.bot.id
        
        if not is_mentioned and not is_reply_to_bot:
            return
        
        # Clean the message (remove mention)
        cleaned_message = message_text.replace(f"@{bot_username}", "").strip()
    
    if not cleaned_message:
        return
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        # Add random delay for human-like response
        await asyncio.sleep(random.uniform(1, 3))
        
        # Initialize user memory if needed
        user_id_str = str(user.id)
        if user_id_str not in chat_memory['messages']:
            chat_memory['messages'][user_id_str] = []
            chat_memory['user_info'][user_id_str] = {}
        
        # Add message to history
        chat_memory['messages'][user_id_str].append(cleaned_message)
        if len(chat_memory['messages'][user_id_str]) > 20:
            chat_memory['messages'][user_id_str].pop(0)
        
        # Get AI response
        response = await get_ai_response(
            cleaned_message,
            chat_memory['messages'][user_id_str],
            chat_memory['user_info'][user_id_str]
        )
        
        if not response:
            await update.message.reply_text(
                "Hmm, laisse-moi réfléchir... 🤔\n"
                "J'ai du mal à traiter ta demande pour le moment.",
                reply_to_message_id=update.message.message_id
            )
            return
        
        # Send response
        await update.message.reply_text(
            response,
            reply_to_message_id=update.message.message_id
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot response: {e}")
        try:
            await update.message.reply_text(
                "Oups! 😅 Je me suis un peu perdu là. Tu peux réessayer ?",
                reply_to_message_id=update.message.message_id
            )
        except:
            pass

async def get_ai_response(user_message, message_history, user_info):
    """Get AI response using PrinceTech GPT API"""
    try:
        # Build context
        context_messages = "\n".join(message_history[-5:]) if message_history else ""
        
        prompt = f"""Tu es NICE-BOT, un assistant IA sympathique et naturel sur Telegram.

RÈGLES IMPORTANTES:
1. Réponds de manière courte et naturelle (1-2 lignes max)
2. Utilise des emojis naturellement
3. Sois amical et décontracté
4. Adapte-toi au ton de l'utilisateur
5. Si l'utilisateur est impoli, reste poli mais ferme

CONTEXTE DES MESSAGES PRÉCÉDENTS:
{context_messages}

MESSAGE ACTUEL: {user_message}

Réponds naturellement:"""
        
        # Use PrinceTech GPT API
        api_key = os.getenv("PRINCETECHN_API_KEY", "prince")
        url = f"https://api.princetechn.com/api/ai/gpt"
        
        async with aiohttp.ClientSession() as session:
            params = {
                "apikey": api_key,
                "q": prompt
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('result'):
                        return data['result'].strip()
        
        return None
        
    except Exception as e:
        logger.error(f"AI API error: {e}")
        return None
