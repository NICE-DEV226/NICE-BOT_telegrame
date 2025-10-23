"""
NICE-BOT - AI Commands
/ai, /resume, /idee commands using PrinceTech GPT API
"""

import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, add_history

logger = logging.getLogger(__name__)

# PrinceTech AI API
PRINCETECH_AI_API = "https://api.princetechn.com/api/ai/gpt"
PRINCETECH_API_KEY = os.getenv("PRINCETECHN_API_KEY", "prince")

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command - AI question answering using PrinceTech GPT"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/ai', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /ai <question>\n\n"
            "**Exemple :** /ai Comment fonctionne l'intelligence artificielle ?\n"
            "**Exemple :** /ai Explique-moi la photosynthèse\n"
            "**Exemple :** /ai Quelle est la capitale de la France ?",
            parse_mode='Markdown'
        )
        return
    
    question = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        async with aiohttp.ClientSession() as session:
            # Use PrinceTech GPT API
            params = {
                "apikey": PRINCETECH_API_KEY,
                "q": question
            }
            
            async with session.get(PRINCETECH_AI_API, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response is successful
                    if data.get('success') and data.get('result'):
                        ai_response = data['result']
                        
                        response_text = f"""
🤖 **Réponse IA**

**Question :** {question}

**Réponse :** {ai_response}

✨ *Propulsé par NICE-BOT AI*
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(
                            "🤖 Désolé, je n'ai pas pu générer une réponse appropriée à votre question.\n"
                            "Réessayez avec une question différente.",
                            parse_mode='Markdown'
                        )
                else:
                    await update.message.reply_text("❌ Service IA temporairement indisponible. Réessayez plus tard.")
    
    except Exception as e:
        logger.error(f"AI error: {e}")
        await update.message.reply_text("❌ Erreur lors de la génération de la réponse IA.")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resume command - Text summarization using PrinceTech AI"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/resume', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /resume <texte à résumer>\n\n"
            "**Exemple :** /resume L'intelligence artificielle est une technologie qui permet aux machines d'apprendre et de prendre des décisions...",
            parse_mode='Markdown'
        )
        return
    
    text_to_summarize = ' '.join(context.args)
    
    if len(text_to_summarize) < 50:
        await update.message.reply_text("❌ Le texte est trop court pour être résumé (minimum 50 caractères).")
        return
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        async with aiohttp.ClientSession() as session:
            # Use PrinceTech GPT API with summarization prompt
            prompt = f"Résume ce texte de manière concise et claire: {text_to_summarize}"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "q": prompt
            }
            
            async with session.get(PRINCETECH_AI_API, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        summary = data['result']
                        
                        response_text = f"""
📝 **Résumé automatique**

**Texte original ({len(text_to_summarize)} caractères) :**
{text_to_summarize[:200]}{'...' if len(text_to_summarize) > 200 else ''}

**Résumé ({len(summary)} caractères) :**
{summary}

✨ *Résumé généré par NICE-BOT AI*
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        await update.message.reply_text("❌ Impossible de générer un résumé pour ce texte.")
                else:
                    await update.message.reply_text("❌ Service de résumé temporairement indisponible.")
    
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        await update.message.reply_text("❌ Erreur lors de la génération du résumé.")

async def idee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /idee command - Idea generation using PrinceTech AI"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/idee', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /idee <sujet>\n\n"
            "**Exemple :** /idee application mobile\n"
            "**Exemple :** /idee projet weekend\n"
            "**Exemple :** /idee cadeau anniversaire",
            parse_mode='Markdown'
        )
        return
    
    topic = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        async with aiohttp.ClientSession() as session:
            # Use PrinceTech GPT API with idea generation prompt
            prompt = f"Donne-moi 5 idées créatives et originales pour: {topic}"
            params = {
                "apikey": PRINCETECH_API_KEY,
                "q": prompt
            }
            
            async with session.get(PRINCETECH_AI_API, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        ideas = data['result']
                        
                        response_text = f"""
💡 **Générateur d'idées**

**Sujet :** {topic}

**Idées générées par IA :**
{ideas}

✨ *Propulsé par NICE-BOT AI - Laissez libre cours à votre créativité !*
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        # Fallback to predefined ideas
                        response_text = await generate_fallback_ideas(topic)
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                else:
                    # Fallback to predefined ideas
                    response_text = await generate_fallback_ideas(topic)
                    await update.message.reply_text(response_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Idea generation error: {e}")
        # Fallback to predefined ideas
        response_text = await generate_fallback_ideas(topic)
        await update.message.reply_text(response_text, parse_mode='Markdown')

async def generate_fallback_ideas(topic: str) -> str:
    """Generate fallback ideas when AI is not available"""
    
    # Predefined idea templates based on common topics
    idea_templates = {
        'app': [
            "Application de suivi des habitudes quotidiennes",
            "App de partage de recettes entre voisins",
            "Outil de gestion de budget personnel",
            "App de méditation guidée",
            "Plateforme d'échange de services locaux"
        ],
        'projet': [
            "Créer un blog sur votre passion",
            "Organiser un événement communautaire",
            "Développer une compétence créative",
            "Lancer un potager urbain",
            "Créer une chaîne YouTube éducative"
        ],
        'cadeau': [
            "Expérience personnalisée (cours, atelier)",
            "Album photo avec souvenirs partagés",
            "Objet fait main avec une touche personnelle",
            "Abonnement à un service qu'ils aiment",
            "Journée d'activités surprises"
        ]
    }
    
    # Find matching category
    topic_lower = topic.lower()
    selected_ideas = []
    
    for category, ideas in idea_templates.items():
        if category in topic_lower:
            selected_ideas = ideas
            break
    
    # Default generic ideas
    if not selected_ideas:
        selected_ideas = [
            f"Rechercher les tendances actuelles en {topic}",
            f"Créer une communauté autour de {topic}",
            f"Développer un guide pratique sur {topic}",
            f"Organiser un événement lié à {topic}",
            f"Innover en combinant {topic} avec la technologie"
        ]
    
    ideas_text = "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(selected_ideas)])
    
    return f"""
💡 **Générateur d'idées**

**Sujet :** {topic}

**Idées suggérées :**
{ideas_text}

*Idées prédéfinies - Personnalisez-les selon vos besoins !*
    """
