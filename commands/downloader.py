#!/usr/bin/env python3
"""
NICE-BOT - Downloader Commands
Video and APK download commands using PrinceTech APIs
"""

import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, add_history

logger = logging.getLogger(__name__)

# PrinceTech API configuration
PRINCETECH_API_KEY = os.getenv("PRINCETECHN_API_KEY", "prince")
PRINCETECH_BASE = "https://api.princetechn.com/api/download"

async def tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tiktok command - Download TikTok videos"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/tiktok', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║   📱 TIKTOK DOWNLOADER    ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/tiktok <url>`\n\n"
            "**Exemple :**\n"
            "`/tiktok https://vm.tiktok.com/ZMrgKWmVd`\n\n"
            "✨ *Téléchargez vos vidéos TikTok préférées !*",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    try:
        await update.message.reply_chat_action("upload_video")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/tiktokdlv3"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "url": url
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        video_url = result.get('video') or result.get('videoUrl')
                        
                        if video_url:
                            # Send video info
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║   📱 TIKTOK DOWNLOAD      ║\n"
                                "╚════════════════════════════╝\n\n"
                                f"**Titre :** {result.get('title', 'N/A')[:100]}\n"
                                f"**Auteur :** {result.get('author', 'N/A')}\n"
                                f"**Durée :** {result.get('duration', 'N/A')}\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            # Send video
                            await update.message.reply_video(
                                video=video_url,
                                caption="✅ **Téléchargé par NICE-BOT**",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Erreur de téléchargement**\n\n"
                    "Impossible de télécharger cette vidéo.\n"
                    "Vérifiez que l'URL est correcte.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"TikTok download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )

async def facebook_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /facebook command - Download Facebook videos"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/facebook', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║  📘 FACEBOOK DOWNLOADER   ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/facebook <url>`\n\n"
            "**Exemple :**\n"
            "`/facebook https://www.facebook.com/reel/123456`\n\n"
            "✨ *Téléchargez des vidéos Facebook !*",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    try:
        await update.message.reply_chat_action("upload_video")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/facebook"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "url": url
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        video_url = result.get('hd') or result.get('sd') or result.get('video')
                        
                        if video_url:
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║  📘 FACEBOOK DOWNLOAD     ║\n"
                                "╚════════════════════════════╝\n\n"
                                f"**Qualité :** {'HD' if result.get('hd') else 'SD'}\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            await update.message.reply_video(
                                video=video_url,
                                caption="✅ **Téléchargé par NICE-BOT**",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Erreur de téléchargement**\n\n"
                    "Impossible de télécharger cette vidéo.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"Facebook download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )

async def instagram_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /instagram command - Download Instagram videos/reels"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/instagram', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║  📸 INSTAGRAM DOWNLOADER  ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/instagram <url>`\n\n"
            "**Exemple :**\n"
            "`/instagram https://www.instagram.com/reel/ABC123`\n\n"
            "✨ *Téléchargez des reels et vidéos Instagram !*",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    try:
        await update.message.reply_chat_action("upload_video")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/instadl"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "url": url
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        media_url = result.get('url') or result.get('video')
                        
                        if media_url:
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║  📸 INSTAGRAM DOWNLOAD    ║\n"
                                "╚════════════════════════════╝\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            await update.message.reply_video(
                                video=media_url,
                                caption="✅ **Téléchargé par NICE-BOT**",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Erreur de téléchargement**\n\n"
                    "Impossible de télécharger ce contenu.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"Instagram download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )

async def twitter_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /twitter command - Download Twitter videos"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/twitter', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║   🐦 TWITTER DOWNLOADER   ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/twitter <url>`\n\n"
            "**Exemple :**\n"
            "`/twitter https://twitter.com/user/status/123`\n\n"
            "✨ *Téléchargez des vidéos Twitter/X !*",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    try:
        await update.message.reply_chat_action("upload_video")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/twitter"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "url": url
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        video_url = result.get('video') or result.get('url')
                        
                        if video_url:
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║   🐦 TWITTER DOWNLOAD     ║\n"
                                "╚════════════════════════════╝\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            await update.message.reply_video(
                                video=video_url,
                                caption="✅ **Téléchargé par NICE-BOT**",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Erreur de téléchargement**\n\n"
                    "Impossible de télécharger cette vidéo.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"Twitter download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )

async def pinterest_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pinterest command - Download Pinterest videos"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/pinterest', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║  📌 PINTEREST DOWNLOADER  ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/pinterest <url>`\n\n"
            "**Exemple :**\n"
            "`/pinterest https://pin.it/ABC123`\n\n"
            "✨ *Téléchargez des vidéos Pinterest !*",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    try:
        await update.message.reply_chat_action("upload_video")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/pinterestdl"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "url": url
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        media_url = result.get('video') or result.get('url')
                        
                        if media_url:
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║  📌 PINTEREST DOWNLOAD    ║\n"
                                "╚════════════════════════════╝\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            await update.message.reply_video(
                                video=media_url,
                                caption="✅ **Téléchargé par NICE-BOT**",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Erreur de téléchargement**\n\n"
                    "Impossible de télécharger ce contenu.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"Pinterest download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )

async def apk_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /apk command - Download APK files"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/apk', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║    📦 APK DOWNLOADER      ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/apk <nom_application>`\n\n"
            "**Exemples :**\n"
            "`/apk WhatsApp`\n"
            "`/apk Instagram`\n"
            "`/apk TikTok`\n\n"
            "✨ *Téléchargez des fichiers APK !*",
            parse_mode='Markdown'
        )
        return
    
    app_name = ' '.join(context.args)
    
    try:
        await update.message.reply_chat_action("upload_document")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{PRINCETECH_BASE}/apkdl"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "appName": app_name
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        apk_url = result.get('dllink') or result.get('download')
                        
                        if apk_url:
                            info_text = (
                                "╔════════════════════════════╗\n"
                                "║    📦 APK DOWNLOAD        ║\n"
                                "╚════════════════════════════╝\n\n"
                                f"**Application :** {result.get('name', app_name)}\n"
                                f"**Version :** {result.get('version', 'N/A')}\n"
                                f"**Taille :** {result.get('size', 'N/A')}\n\n"
                                "⏳ *Téléchargement en cours...*"
                            )
                            await update.message.reply_text(info_text, parse_mode='Markdown')
                            
                            await update.message.reply_document(
                                document=apk_url,
                                caption=f"✅ **{result.get('name', app_name)}**\n📦 *Téléchargé par NICE-BOT*",
                                parse_mode='Markdown'
                            )
                            return
                
                await update.message.reply_text(
                    "❌ **Application non trouvée**\n\n"
                    "Vérifiez le nom de l'application et réessayez.",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"APK download error: {e}")
        await update.message.reply_text(
            "❌ **Erreur**\n\n"
            "Une erreur s'est produite lors du téléchargement.",
            parse_mode='Markdown'
        )
