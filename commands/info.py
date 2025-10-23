"""
NICE-BOT - Info & Fun Commands
/citation, /blague, /film, /news, /wiki commands
"""

import os
import logging
import aiohttp
import random
import json
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from db import get_user, add_history

logger = logging.getLogger(__name__)

# Load local citations database
CITATIONS_FILE = Path(__file__).parent.parent / "data" / "citations.json"
LOCAL_CITATIONS = []

try:
    if CITATIONS_FILE.exists():
        with open(CITATIONS_FILE, 'r', encoding='utf-8') as f:
            LOCAL_CITATIONS = json.load(f)
        logger.info(f"Loaded {len(LOCAL_CITATIONS)} local citations")
except Exception as e:
    logger.error(f"Error loading local citations: {e}")
    LOCAL_CITATIONS = []

# Load local jokes database
BLAGUES_FILE = Path(__file__).parent.parent / "data" / "blagues.json"
LOCAL_BLAGUES = []

try:
    if BLAGUES_FILE.exists():
        with open(BLAGUES_FILE, 'r', encoding='utf-8') as f:
            LOCAL_BLAGUES = json.load(f)
        logger.info(f"Loaded {len(LOCAL_BLAGUES)} local jokes")
except Exception as e:
    logger.error(f"Error loading local jokes: {e}")
    LOCAL_BLAGUES = []

async def citation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /citation command - Inspirational quotes from local database"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/citation')
    
    try:
        # Use local citations database first
        if LOCAL_CITATIONS:
            citation_data = random.choice(LOCAL_CITATIONS)
            quote = citation_data['quote']
            author = citation_data['author']
            
            response_text = f"""
✨ **Citation inspirante**

*"{quote}"*

**— {author}**

🌟 Partagez cette inspiration !
🐍 *Base locale Python - {len(LOCAL_CITATIONS)} citations*
            """
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
            return
        
        # Fallback to API if local database not available
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as response:
                if response.status == 200:
                    data = await response.json()
                    quote = data['content']
                    author = data['author']
                    
                    response_text = f"""
✨ **Citation inspirante**

*"{quote}"*

**— {author}**

🌟 Partagez cette inspiration !
                    """
                    
                    await update.message.reply_text(response_text, parse_mode='Markdown')
                else:
                    # Fallback quotes
                    await send_fallback_quote(update)
    
    except Exception as e:
        logger.error(f"Quote error: {e}")
        await send_fallback_quote(update)

async def send_fallback_quote(update):
    """Send a fallback quote when API is unavailable"""
    fallback_quotes = [
        ("La seule façon de faire du bon travail est d'aimer ce que vous faites.", "Steve Jobs"),
        ("L'innovation distingue un leader d'un suiveur.", "Steve Jobs"),
        ("La vie, c'est comme une bicyclette, il faut avancer pour ne pas perdre l'équilibre.", "Albert Einstein"),
        ("Le succès, c'est d'aller d'échec en échec sans perdre son enthousiasme.", "Winston Churchill"),
        ("Il n'y a qu'une façon d'échouer, c'est d'abandonner avant d'avoir réussi.", "Georges Clemenceau")
    ]
    
    quote, author = random.choice(fallback_quotes)
    
    response_text = f"""
✨ **Citation inspirante**

*"{quote}"*

**— {author}**

🌟 Partagez cette inspiration !
    """
    
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def blague(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /blague command - Random jokes from local database"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/blague')
    
    try:
        # Use local jokes database first
        if LOCAL_BLAGUES:
            joke = random.choice(LOCAL_BLAGUES)
            
            response_text = f"""
😂 **Blague du jour**

{joke}

🎭 Bonne humeur garantie !
🐍 *Base locale Python - {len(LOCAL_BLAGUES)} blagues*
            """
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
            return
        
        # Fallback to API if local database not available
        async with aiohttp.ClientSession() as session:
            # Get a safe joke in French if possible, otherwise English
            url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('type') == 'single':
                        joke = data['joke']
                        
                        response_text = f"""
😂 **Blague du jour**

{joke}

🎭 Bonne humeur garantie !
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        await send_fallback_joke(update)
                else:
                    await send_fallback_joke(update)
    
    except Exception as e:
        logger.error(f"Joke error: {e}")
        await send_fallback_joke(update)

async def send_fallback_joke(update):
    """Send a fallback joke when API is unavailable"""
    fallback_jokes = [
        "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon, ils tombent dans le bateau !",
        "Que dit un escargot quand il croise une limace ? 'Regarde, un nudiste !'",
        "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-mallow !",
        "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet !",
        "Que dit un informaticien quand il se noie ? F1 ! F1 !",
        "Comment appelle-t-on un boomerang qui ne revient pas ? Un bâton !",
        "Pourquoi les développeurs préfèrent-ils le mode sombre ? Parce que la lumière attire les bugs !"
    ]
    
    joke = random.choice(fallback_jokes)
    
    response_text = f"""
😂 **Blague du jour**

{joke}

🎭 Bonne humeur garantie !
    """
    
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /film command - Movie search using TMDB"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/film', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /film <nom du film>\n\n"
            "**Exemple :** /film Inception\n"
            "**Exemple :** /film Le Seigneur des Anneaux",
            parse_mode='Markdown'
        )
        return
    
    movie_name = ' '.join(context.args)
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    
    if not tmdb_api_key:
        await update.message.reply_text("❌ Service de recherche de films temporairement indisponible.")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            # Search for movie
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={movie_name}&language=fr-FR"
            
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data['results']:
                        movie = data['results'][0]  # Get first result
                        
                        title = movie.get('title', 'N/A')
                        original_title = movie.get('original_title', '')
                        overview = movie.get('overview', 'Pas de description disponible.')
                        release_date = movie.get('release_date', 'N/A')
                        vote_average = movie.get('vote_average', 0)
                        vote_count = movie.get('vote_count', 0)
                        
                        # Format rating stars
                        stars = "⭐" * int(vote_average / 2) if vote_average > 0 else "❓"
                        
                        response_text = f"""
🎬 **Informations sur le film**

**Titre :** {title}
{f"**Titre original :** {original_title}" if original_title != title else ""}

**Synopsis :**
{overview[:300]}{'...' if len(overview) > 300 else ''}

**Date de sortie :** {release_date}
**Note :** {vote_average}/10 {stars} ({vote_count} votes)

*Données fournies par TMDB*
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"❌ Aucun film trouvé pour '{movie_name}'.")
                else:
                    await update.message.reply_text("❌ Erreur lors de la recherche de films.")
    
    except Exception as e:
        logger.error(f"Movie search error: {e}")
        await update.message.reply_text("❌ Erreur lors de la recherche de films.")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /news command - Latest news using PrinceTech Wikimedia"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/news', ' '.join(context.args) if context.args else '')
    
    # Default topics if no argument provided
    default_topics = ["Technology", "Science", "World News", "Business", "Sports"]
    
    if not context.args:
        await update.message.reply_text(
            "📰 **Actualités**\n\n"
            "**Usage :** `/news <sujet>`\n\n"
            "**Exemples :**\n"
            "• `/news Elon Musk`\n"
            "• `/news Intelligence artificielle`\n"
            "• `/news Football`\n"
            "• `/news Bitcoin`\n\n"
            "💡 **Astuce :** Recherchez n'importe quel sujet d'actualité !",
            parse_mode='Markdown'
        )
        return
    
    topic = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        async with aiohttp.ClientSession() as session:
            # Use PrinceTech Wikimedia API
            princetechn_api_key = os.getenv("PRINCETECHN_API_KEY", "prince")
            url = f"https://api.princetechn.com/api/search/wikimedia"
            params = {
                "apikey": princetechn_api_key,
                "title": topic
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('result'):
                        result = data['result']
                        
                        # Extract information
                        title = result.get('title', topic)
                        extract = result.get('extract', 'Aucune information disponible.')
                        thumbnail = result.get('thumbnail', {}).get('source', '')
                        page_url = result.get('content_urls', {}).get('desktop', {}).get('page', '')
                        
                        response_text = f"""
📰 **Actualités - {title}**

{extract[:500]}{'...' if len(extract) > 500 else ''}

🔗 **Plus d'infos :** {page_url if page_url else 'Non disponible'}

✨ *Propulsé par NICE-BOT*
                        """
                        
                        await update.message.reply_text(response_text, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(
                            f"❌ Aucune actualité trouvée pour '{topic}'.\n\n"
                            "Essayez avec un autre sujet ou un nom plus précis.",
                            parse_mode='Markdown'
                        )
                else:
                    await update.message.reply_text("❌ Erreur lors de la récupération des actualités.")
    
    except Exception as e:
        logger.error(f"News error: {e}")
        await update.message.reply_text("❌ Erreur lors de la récupération des actualités.")

async def wiki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wiki command - Wikipedia search"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/wiki', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /wiki <terme de recherche>\n\n"
            "**Exemple :** /wiki Intelligence artificielle\n"
            "**Exemple :** /wiki Python programmation",
            parse_mode='Markdown'
        )
        return
    
    search_term = ' '.join(context.args)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Search Wikipedia in French
            search_url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{search_term}"
            
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    title = data.get('title', search_term)
                    extract = data.get('extract', 'Aucun résumé disponible.')
                    page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    
                    # Get thumbnail if available
                    thumbnail = data.get('thumbnail', {}).get('source', '')
                    
                    response_text = f"""
📖 **Wikipédia - {title}**

{extract}

🔗 **Lien complet :** {page_url}

*Source : Wikipédia*
                    """
                    
                    await update.message.reply_text(response_text, parse_mode='Markdown')
                    
                elif response.status == 404:
                    # Try search API if direct page not found
                    search_api_url = f"https://fr.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={search_term}&srlimit=1"
                    
                    async with session.get(search_api_url) as search_response:
                        if search_response.status == 200:
                            search_data = await search_response.json()
                            
                            if search_data.get('query', {}).get('search'):
                                page_title = search_data['query']['search'][0]['title']
                                snippet = search_data['query']['search'][0]['snippet']
                                
                                # Remove HTML tags from snippet
                                import re
                                clean_snippet = re.sub('<.*?>', '', snippet)
                                
                                response_text = f"""
📖 **Wikipédia - {page_title}**

{clean_snippet}...

🔗 **Lien :** https://fr.wikipedia.org/wiki/{page_title.replace(' ', '_')}

*Source : Wikipédia*
                                """
                                
                                await update.message.reply_text(response_text, parse_mode='Markdown')
                            else:
                                await update.message.reply_text(f"❌ Aucun article trouvé pour '{search_term}' sur Wikipédia.")
                        else:
                            await update.message.reply_text("❌ Erreur lors de la recherche sur Wikipédia.")
                else:
                    await update.message.reply_text("❌ Erreur lors de la recherche sur Wikipédia.")
    
    except Exception as e:
        logger.error(f"Wikipedia error: {e}")
        await update.message.reply_text("❌ Erreur lors de la recherche sur Wikipédia.")

async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /meme command - Random meme from Reddit"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/meme')
    
    try:
        # Send typing action
        await update.message.reply_chat_action("upload_photo")
        
        async with aiohttp.ClientSession() as session:
            # Get random meme from Reddit API
            api_url = "https://meme-api.com/gimme"
            
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract meme data
                    title = data.get('title', 'Meme sans titre')
                    url = data.get('url', '')
                    subreddit = data.get('subreddit', 'unknown')
                    author = data.get('author', 'unknown')
                    ups = data.get('ups', 0)
                    post_link = data.get('postLink', '')
                    nsfw = data.get('nsfw', False)
                    spoiler = data.get('spoiler', False)
                    
                    # Check if content is appropriate
                    if nsfw:
                        await update.message.reply_text(
                            "🔞 **Contenu NSFW détecté**\n\n"
                            "Ce meme contient du contenu pour adultes et ne peut pas être affiché.\n"
                            "Réessayez pour obtenir un autre meme !",
                            parse_mode='Markdown'
                        )
                        return
                    
                    # Prepare caption
                    caption = f"""
😂 **{title}**

📱 **Subreddit :** r/{subreddit}
👤 **Auteur :** u/{author}
⬆️ **Upvotes :** {ups:,}
{'⚠️ **Spoiler**' if spoiler else ''}

🔗 [Voir sur Reddit]({post_link})
                    """
                    
                    # Send meme
                    if url.endswith(('.gif', '.mp4', '.webm')):
                        # Send as animation/video
                        await update.message.reply_animation(
                            animation=url,
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        # Send as photo
                        await update.message.reply_photo(
                            photo=url,
                            caption=caption,
                            parse_mode='Markdown'
                        )
                        
                else:
                    await update.message.reply_text(
                        "❌ **Erreur API Meme**\n\n"
                        "Impossible de récupérer un meme pour le moment. Réessayez plus tard !",
                        parse_mode='Markdown'
                    )
    
    except Exception as e:
        logger.error(f"Meme API error: {e}")
        await update.message.reply_text(
            "❌ **Erreur lors de la récupération du meme**\n\n"
            "Une erreur technique s'est produite. Réessayez plus tard !",
            parse_mode='Markdown'
        )
