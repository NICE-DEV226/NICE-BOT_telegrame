#!/usr/bin/env python3
"""
NICE-BOT - Channel & Group Management Commands (Admin Only)
Professional management tools for groups and channels
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from db import get_user, add_history

logger = logging.getLogger(__name__)

# Admin user ID from environment
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Data file for managed groups
MANAGED_GROUPS_FILE = Path(__file__).parent.parent / "data" / "managed_groups.json"

def load_managed_groups():
    """Load managed groups data"""
    try:
        MANAGED_GROUPS_FILE.parent.mkdir(exist_ok=True)
        if MANAGED_GROUPS_FILE.exists():
            with open(MANAGED_GROUPS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'groups': {}, 'channels': {}, 'stats': {}}
    except Exception as e:
        logger.error(f"Error loading managed groups: {e}")
        return {'groups': {}, 'channels': {}, 'stats': {}}

def save_managed_groups(data):
    """Save managed groups data"""
    try:
        MANAGED_GROUPS_FILE.parent.mkdir(exist_ok=True)
        with open(MANAGED_GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving managed groups: {e}")

def is_admin(user_id: int) -> bool:
    """Check if user is bot admin"""
    return user_id == ADMIN_USER_ID

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listgroups command - List all groups bot is in (Admin only)"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/listgroups', '')
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║      ACCES REFUSE         ║\n"
            "╚════════════════════════════╝\n\n"
            "Cette commande est reservee aux administrateurs du bot.\n\n"
            f"Votre ID : `{user.id}`",
            parse_mode='Markdown'
        )
        return
    
    try:
        data = load_managed_groups()
        groups = data.get('groups', {})
        channels = data.get('channels', {})
        
        if not groups and not channels:
            await update.message.reply_text(
                "╔════════════════════════════╗\n"
                "║    AUCUN GROUPE/CANAL     ║\n"
                "╚════════════════════════════╝\n\n"
                "Le bot n'est dans aucun groupe ou canal.",
                parse_mode='Markdown'
            )
            return
        
        response = "╔════════════════════════════════════╗\n"
        response += "║   GROUPES ET CANAUX GERES        ║\n"
        response += "╚════════════════════════════════════╝\n\n"
        
        if groups:
            response += f"**GROUPES ({len(groups)}) :**\n\n"
            for chat_id, info in list(groups.items())[:20]:
                response += f"• **{info.get('name', 'N/A')}**\n"
                response += f"  ID: `{chat_id}`\n"
                response += f"  Membres: {info.get('member_count', 'N/A')}\n"
                response += f"  Ajoute: {info.get('added_at', 'N/A')[:10]}\n\n"
            
            if len(groups) > 20:
                response += f"... et {len(groups) - 20} autres groupes\n\n"
        
        if channels:
            response += f"**CANAUX ({len(channels)}) :**\n\n"
            for chat_id, info in list(channels.items())[:10]:
                response += f"• **{info.get('name', 'N/A')}**\n"
                response += f"  ID: `{chat_id}`\n"
                response += f"  Ajoute: {info.get('added_at', 'N/A')[:10]}\n\n"
        
        response += f"**TOTAL : {len(groups) + len(channels)} groupes/canaux**"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error listing groups: {e}")
        await update.message.reply_text(
            "Erreur lors de la recuperation de la liste.",
            parse_mode='Markdown'
        )

async def leave_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leavegroup command - Leave a specific group (Admin only)"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/leavegroup', ' '.join(context.args))
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║      ACCES REFUSE         ║\n"
            "╚════════════════════════════╝\n\n"
            "Cette commande est reservee aux administrateurs du bot.",
            parse_mode='Markdown'
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║    QUITTER UN GROUPE      ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/leavegroup <chat_id>`\n\n"
            "**Exemple :**\n"
            "`/leavegroup -1001234567890`\n\n"
            "Utilisez `/listgroups` pour voir les IDs.",
            parse_mode='Markdown'
        )
        return
    
    try:
        chat_id = int(context.args[0])
        
        # Try to leave the chat
        await context.bot.leave_chat(chat_id)
        
        # Remove from managed groups
        data = load_managed_groups()
        chat_id_str = str(chat_id)
        
        if chat_id_str in data.get('groups', {}):
            group_name = data['groups'][chat_id_str].get('name', 'N/A')
            del data['groups'][chat_id_str]
            save_managed_groups(data)
            
            await update.message.reply_text(
                "╔════════════════════════════╗\n"
                "║      GROUPE QUITTE        ║\n"
                "╚════════════════════════════╝\n\n"
                f"**Groupe :** {group_name}\n"
                f"**ID :** `{chat_id}`\n\n"
                "Le bot a quitte le groupe avec succes.",
                parse_mode='Markdown'
            )
        elif chat_id_str in data.get('channels', {}):
            channel_name = data['channels'][chat_id_str].get('name', 'N/A')
            del data['channels'][chat_id_str]
            save_managed_groups(data)
            
            await update.message.reply_text(
                "╔════════════════════════════╗\n"
                "║      CANAL QUITTE         ║\n"
                "╚════════════════════════════╝\n\n"
                f"**Canal :** {channel_name}\n"
                f"**ID :** `{chat_id}`\n\n"
                "Le bot a quitte le canal avec succes.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "Le bot a quitte le chat (ID non trouve dans la base).",
                parse_mode='Markdown'
            )
    
    except ValueError:
        await update.message.reply_text(
            "ID de chat invalide. Utilisez un nombre.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error leaving group: {e}")
        await update.message.reply_text(
            f"Erreur : {str(e)}\n\n"
            "Verifiez que l'ID est correct.",
            parse_mode='Markdown'
        )

async def broadcast_to_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcastgroups command - Broadcast to all groups (Admin only)"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/broadcastgroups', ' '.join(context.args))
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║      ACCES REFUSE         ║\n"
            "╚════════════════════════════╝\n\n"
            "Cette commande est reservee aux administrateurs du bot.",
            parse_mode='Markdown'
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║    BROADCAST GROUPES      ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/broadcastgroups <message>`\n\n"
            "**Exemple :**\n"
            "`/broadcastgroups Mise a jour importante !`\n\n"
            "**Attention :** Envoie a TOUS les groupes.",
            parse_mode='Markdown'
        )
        return
    
    message = ' '.join(context.args)
    
    try:
        data = load_managed_groups()
        groups = data.get('groups', {})
        
        if not groups:
            await update.message.reply_text(
                "Aucun groupe a qui envoyer le message.",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            f"Envoi en cours vers {len(groups)} groupes...",
            parse_mode='Markdown'
        )
        
        success_count = 0
        failed_count = 0
        
        for chat_id in groups.keys():
            try:
                await context.bot.send_message(
                    chat_id=int(chat_id),
                    text=f"**ANNONCE NICE-BOT**\n\n{message}",
                    parse_mode='Markdown'
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
                failed_count += 1
        
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║    BROADCAST TERMINE      ║\n"
            "╚════════════════════════════╝\n\n"
            f"**Envoyes :** {success_count}\n"
            f"**Echecs :** {failed_count}\n"
            f"**Total :** {len(groups)} groupes",
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Error broadcasting to groups: {e}")
        await update.message.reply_text(
            f"Erreur lors du broadcast : {str(e)}",
            parse_mode='Markdown'
        )

async def group_stats_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /groupstats command - Statistics about groups (Admin only)"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/groupstats', '')
    
    # Check if user is admin
    if not is_admin(user.id):
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║      ACCES REFUSE         ║\n"
            "╚════════════════════════════╝\n\n"
            "Cette commande est reservee aux administrateurs du bot.",
            parse_mode='Markdown'
        )
        return
    
    try:
        data = load_managed_groups()
        groups = data.get('groups', {})
        channels = data.get('channels', {})
        
        # Calculate stats
        total_members = sum(g.get('member_count', 0) for g in groups.values())
        avg_members = total_members // len(groups) if groups else 0
        
        # Find largest group
        largest_group = max(groups.items(), key=lambda x: x[1].get('member_count', 0)) if groups else None
        
        stats_text = "╔════════════════════════════════════╗\n"
        stats_text += "║   STATISTIQUES GROUPES/CANAUX    ║\n"
        stats_text += "╚════════════════════════════════════╝\n\n"
        
        stats_text += "**RESUME GENERAL :**\n\n"
        stats_text += f"• Groupes : {len(groups)}\n"
        stats_text += f"• Canaux : {len(channels)}\n"
        stats_text += f"• Total : {len(groups) + len(channels)}\n\n"
        
        if groups:
            stats_text += "**STATISTIQUES GROUPES :**\n\n"
            stats_text += f"• Membres totaux : {total_members:,}\n"
            stats_text += f"• Moyenne/groupe : {avg_members}\n"
            
            if largest_group:
                stats_text += f"• Plus grand groupe :\n"
                stats_text += f"  {largest_group[1].get('name', 'N/A')}\n"
                stats_text += f"  ({largest_group[1].get('member_count', 0)} membres)\n\n"
        
        stats_text += "**COMMANDES DISPONIBLES :**\n\n"
        stats_text += "• `/listgroups` - Liste complete\n"
        stats_text += "• `/leavegroup <id>` - Quitter un groupe\n"
        stats_text += "• `/broadcastgroups <msg>` - Broadcast\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error getting group stats: {e}")
        await update.message.reply_text(
            "Erreur lors de la recuperation des statistiques.",
            parse_mode='Markdown'
        )
