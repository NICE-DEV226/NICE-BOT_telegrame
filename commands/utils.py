"""
NICE-BOT - Utility Commands
/traduire, /meteo, /devise, /qr, /pdf commands
"""

import os
import io
import logging
import aiohttp
import qrcode
from fpdf import FPDF
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from db import get_user, add_history

logger = logging.getLogger(__name__)

async def traduire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /traduire command - Advanced translation with reply support and multiple APIs"""
    from urllib.parse import quote
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/traduire', ' '.join(context.args))
    
    text_to_translate = ''
    target_lang = 'fr'  # Default target language
    
    # Check if it's a reply to a message
    if update.message.reply_to_message:
        # Get text from replied message
        replied_msg = update.message.reply_to_message
        text_to_translate = replied_msg.text or replied_msg.caption or ''
        
        # Get target language from command args
        if context.args:
            target_lang = context.args[0].lower()
    else:
        # Parse command arguments
        if not context.args:
            await update.message.reply_text(
                "🌐 **TRADUCTEUR AVANCÉ**\n\n"
                "**Usage :**\n"
                "1️⃣ Répondre à un message : `/traduire <langue>`\n"
                "2️⃣ Texte direct : `/traduire <texte> <langue>`\n\n"
                "**Exemples :**\n"
                "• `/traduire Hello world fr`\n"
                "• `/traduire Bonjour en`\n"
                "• Répondre à un message + `/traduire en`\n\n"
                "**Codes de langue :**\n"
                "🇫🇷 `fr` - Français | 🇬🇧 `en` - Anglais\n"
                "🇪🇸 `es` - Espagnol | 🇩🇪 `de` - Allemand\n"
                "🇮🇹 `it` - Italien | 🇵🇹 `pt` - Portugais\n"
                "🇷🇺 `ru` - Russe | 🇯🇵 `ja` - Japonais\n"
                "🇰🇷 `ko` - Coréen | 🇨🇳 `zh` - Chinois\n"
                "🇸🇦 `ar` - Arabe | 🇮🇳 `hi` - Hindi",
                parse_mode='Markdown'
            )
            return
        
        # Get language code (last argument)
        args = context.args
        if len(args) >= 2:
            target_lang = args[-1].lower()
            text_to_translate = ' '.join(args[:-1])
        else:
            # Auto-detect: if text looks French, translate to English, else to French
            text_to_translate = ' '.join(args)
            is_french = any(word in text_to_translate.lower() for word in ['le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais'])
            target_lang = 'en' if is_french else 'fr'
    
    if not text_to_translate:
        await update.message.reply_text("❌ Aucun texte à traduire trouvé.")
        return
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        translated_text = None
        api_used = None
        
        async with aiohttp.ClientSession() as session:
            # Try API 1: Google Translate (unofficial)
            try:
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={quote(text_to_translate)}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and data[0] and data[0][0] and data[0][0][0]:
                            translated_text = data[0][0][0]
                            api_used = "Google Translate"
            except Exception as e:
                logger.warning(f"Google Translate API failed: {e}")
            
            # Try API 2: MyMemory
            if not translated_text:
                try:
                    url = f"https://api.mymemory.translated.net/get?q={quote(text_to_translate)}&langpair=auto|{target_lang}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data and data.get('responseData', {}).get('translatedText'):
                                translated_text = data['responseData']['translatedText']
                                api_used = "MyMemory"
                except Exception as e:
                    logger.warning(f"MyMemory API failed: {e}")
            
            # Try API 3: PopCat
            if not translated_text:
                try:
                    url = "https://api.popcat.xyz/v2/translate"
                    params = {"to": target_lang, "text": text_to_translate}
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if not data.get('error', True) and data.get('message', {}).get('translated'):
                                translated_text = data['message']['translated']
                                api_used = "PopCat"
                except Exception as e:
                    logger.warning(f"PopCat API failed: {e}")
            
            # Try API 4: LibreTranslate (fallback)
            if not translated_text:
                try:
                    libretranslate_url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")
                    payload = {
                        "q": text_to_translate,
                        "source": "auto",
                        "target": target_lang
                    }
                    async with session.post(f"{libretranslate_url}/translate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            translated_text = result.get('translatedText')
                            api_used = "LibreTranslate"
                except Exception as e:
                    logger.warning(f"LibreTranslate API failed: {e}")
        
        if not translated_text:
            await update.message.reply_text("❌ Toutes les APIs de traduction ont échoué. Réessayez plus tard.")
            return
        
        # Format response
        response_text = f"""
🌐 **Traduction ({api_used})**

**Texte original :**
{text_to_translate[:200]}{'...' if len(text_to_translate) > 200 else ''}

**Traduction ({target_lang.upper()}) :**
{translated_text}

✨ *Traduction automatique*
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text("❌ Erreur lors de la traduction. Service temporairement indisponible.")

async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /meteo command - Weather using PrinceTech API with Open-Meteo fallback"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/meteo', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /meteo <ville>\n\n"
            "**Exemple :** /meteo Paris\n"
            "**Exemple :** /meteo Kisumu",
            parse_mode='Markdown'
        )
        return
    
    city = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("typing")
        
        async with aiohttp.ClientSession() as session:
            # Try PrinceTech API first (more detailed data)
            try:
                princetechn_api_key = os.getenv("PRINCETECHN_API_KEY", "prince")
                princetechn_url = f"https://api.princetechn.com/api/search/weather?apikey={princetechn_api_key}&location={city}"
                
                async with session.get(princetechn_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success') and data.get('result'):
                            result = data['result']
                            weather = result['weather']
                            main = result['main']
                            wind = result['wind']
                            coord = result['coord']
                            sys = result['sys']
                            
                            # Weather description to emoji mapping
                            weather_emojis = {
                                'clear': "☀️", 'sunny': "☀️", 'clouds': "☁️", 'cloudy': "☁️",
                                'rain': "🌧️", 'drizzle': "🌦️", 'thunderstorm': "⛈️", 'storm': "⛈️",
                                'snow': "❄️", 'mist': "🌫️", 'fog': "🌫️", 'haze': "🌫️"
                            }
                            
                            weather_main = weather['main'].lower()
                            weather_emoji = "🌡️"
                            for key, emoji in weather_emojis.items():
                                if key in weather_main:
                                    weather_emoji = emoji
                                    break
                            
                            # Convert sunrise/sunset timestamps
                            from datetime import datetime
                            sunrise = datetime.fromtimestamp(sys['sunrise']).strftime('%H:%M')
                            sunset = datetime.fromtimestamp(sys['sunset']).strftime('%H:%M')
                            
                            response_text = f"""
{weather_emoji} **Météo - {result['location']}, {sys['country']}**

🌡️ **Température :** {main['temp']:.1f}°C (ressenti {main['feels_like']:.1f}°C)
📊 **Min/Max :** {main['temp_min']:.1f}°C / {main['temp_max']:.1f}°C
🌤️ **Conditions :** {weather['description'].title()}

💨 **Vent :** {wind['speed']} m/s ({wind['deg']}°)
💧 **Humidité :** {main['humidity']}%
🌊 **Pression :** {main['pressure']} hPa
👁️ **Visibilité :** {result['visibility']/1000:.1f} km
☁️ **Nuages :** {result['clouds']}%

🌅 **Lever du soleil :** {sunrise}
🌇 **Coucher du soleil :** {sunset}

📍 **Coordonnées :** {coord['lat']:.2f}, {coord['lon']:.2f}

✨ *Données fournies par NICE-BOT*
                            """
                            
                            await update.message.reply_text(response_text, parse_mode='Markdown')
                            return
                            
            except Exception as princetechn_error:
                logger.warning(f"PrinceTech API failed, trying Open-Meteo: {princetechn_error}")
            
            # Fallback to Open-Meteo API
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            
            async with session.get(geocoding_url) as response:
                if response.status == 200:
                    geo_data = await response.json()
                    if not geo_data.get('results'):
                        await update.message.reply_text(f"❌ Ville '{city}' non trouvée.")
                        return
                    
                    location = geo_data['results'][0]
                    lat, lon = location['latitude'], location['longitude']
                    city_name = location['name']
                    country = location.get('country', '')
                    
                    # Get weather data from Open-Meteo
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
                    
                    async with session.get(weather_url) as weather_response:
                        if weather_response.status == 200:
                            weather_data = await weather_response.json()
                            current = weather_data['current_weather']
                            
                            # Weather code to emoji mapping
                            weather_codes = {
                                0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
                                45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️", 55: "🌦️",
                                61: "🌧️", 63: "🌧️", 65: "🌧️", 80: "🌦️", 81: "🌦️", 82: "🌦️",
                                95: "⛈️", 96: "⛈️", 99: "⛈️"
                            }
                            
                            weather_emoji = weather_codes.get(current['weathercode'], "🌡️")
                            
                            response_text = f"""
{weather_emoji} **Météo - {city_name}, {country}**

🌡️ **Température :** {current['temperature']}°C
💨 **Vent :** {current['windspeed']} km/h
🧭 **Direction :** {current['winddirection']}°

📍 **Coordonnées :** {lat:.2f}, {lon:.2f}
⏰ **Dernière mise à jour :** {current['time']}

🔄 *Service de secours utilisé (Open-Meteo)*
                            """
                            
                            await update.message.reply_text(response_text, parse_mode='Markdown')
                        else:
                            await update.message.reply_text("❌ Erreur lors de la récupération des données météo.")
                else:
                    await update.message.reply_text("❌ Erreur lors de la géolocalisation.")
    

async def devise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /devise command - Currency conversion with built-in rates"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/devise', ' '.join(context.args))
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "╔════════════════════════════╗\n"
            "║   💱 CONVERTISSEUR DE     ║\n"
            "║        DEVISES            ║\n"
            "╚════════════════════════════╝\n\n"
            "**Usage :**\n"
            "`/devise <montant> <de> <vers>`\n\n"
            "**Exemples :**\n"
            "`/devise 100 USD EUR`\n"
            "`/devise 50 EUR GBP`\n"
            "`/devise 1000 XOF EUR`\n\n"
            "**Devises supportées :**\n"
            "💵 USD, EUR, GBP, JPY, CNY\n"
            "💰 CAD, AUD, CHF, INR, RUB\n"
            "🌍 XOF, XAF, MAD, DZD, TND\n"
            "🏦 BTC, ETH (crypto)",
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(context.args[0])
        from_currency = context.args[1].upper()
        to_currency = context.args[2].upper()
        
        # Taux de change par rapport à l'EUR (base)
        exchange_rates = {
            'EUR': 1.0,
            'USD': 1.09,      # Dollar américain
            'GBP': 0.86,      # Livre sterling
            'JPY': 161.50,    # Yen japonais
            'CNY': 7.85,      # Yuan chinois
            'CAD': 1.48,      # Dollar canadien
            'AUD': 1.66,      # Dollar australien
            'CHF': 0.94,      # Franc suisse
            'INR': 90.50,     # Roupie indienne
            'RUB': 100.00,    # Rouble russe
            'XOF': 655.96,    # Franc CFA (BCEAO)
            'XAF': 655.96,    # Franc CFA (BEAC)
            'MAD': 10.80,     # Dirham marocain
            'DZD': 146.50,    # Dinar algérien
            'TND': 3.38,      # Dinar tunisien
            'BRL': 5.42,      # Real brésilien
            'MXN': 18.60,     # Peso mexicain
            'ZAR': 20.30,     # Rand sud-africain
            'KRW': 1450.00,   # Won sud-coréen
            'SGD': 1.45,      # Dollar singapourien
            'HKD': 8.50,      # Dollar de Hong Kong
            'NOK': 11.70,     # Couronne norvégienne
            'SEK': 11.40,     # Couronne suédoise
            'DKK': 7.46,      # Couronne danoise
            'PLN': 4.35,      # Zloty polonais
            'THB': 38.50,     # Baht thaïlandais
            'IDR': 17000.00,  # Roupie indonésienne
            'MYR': 5.10,      # Ringgit malaisien
            'PHP': 61.50,     # Peso philippin
            'BTC': 0.000016,  # Bitcoin
            'ETH': 0.00045,   # Ethereum
        }
        
        # Vérifier si les devises sont supportées
        if from_currency not in exchange_rates:
            await update.message.reply_text(
                f"❌ **Devise non supportée : {from_currency}**\n\n"
                "Utilisez `/devise` sans arguments pour voir la liste des devises.",
                parse_mode='Markdown'
            )
            return
        
        if to_currency not in exchange_rates:
            await update.message.reply_text(
                f"❌ **Devise non supportée : {to_currency}**\n\n"
                "Utilisez `/devise` sans arguments pour voir la liste des devises.",
                parse_mode='Markdown'
            )
            return
        
        # Conversion : montant -> EUR -> devise cible
        amount_in_eur = amount / exchange_rates[from_currency]
        converted_amount = amount_in_eur * exchange_rates[to_currency]
        rate = exchange_rates[to_currency] / exchange_rates[from_currency]
        
        # Déterminer les symboles de devises
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'CNY': '¥', 'INR': '₹', 'RUB': '₽', 'BTC': '₿',
            'XOF': 'CFA', 'XAF': 'CFA', 'MAD': 'DH', 'DZD': 'DA', 'TND': 'DT'
        }
        
        from_symbol = currency_symbols.get(from_currency, from_currency)
        to_symbol = currency_symbols.get(to_currency, to_currency)
        
        response_text = f"""
╔════════════════════════════╗
║   💱 CONVERSION DEVISE    ║
╚════════════════════════════╝

💰 **{amount:,.2f} {from_currency}** ({from_symbol})
        ⬇️
💵 **{converted_amount:,.2f} {to_currency}** ({to_symbol})

📊 **Taux :** 1 {from_currency} = {rate:.4f} {to_currency}

✨ *Conversion par NICE-BOT*
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    except ValueError:
        await update.message.reply_text(
            "❌ **Montant invalide**\n\n"
            "Utilisez un nombre valide.\n"
            "Exemple : `/devise 100 USD EUR`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Currency conversion error: {e}")
        await update.message.reply_text(
            "❌ **Erreur lors de la conversion**\n\n"
            "Vérifiez votre commande et réessayez.",
            parse_mode='Markdown'
        )

async def qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /qr command - QR code generation using QR Server API"""
    user = update.effective_user
    
    # ... (reste du code inchangé)
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/qr', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /qr <texte ou URL>\n\n"
            "**Exemple :** /qr https://google.com\n"
            "**Exemple :** /qr Bonjour le monde !\n"
            "**Exemple :** /qr Contactez-moi: +33123456789",
            parse_mode='Markdown'
        )
        return
    
    text_to_encode = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("upload_photo")
        
        async with aiohttp.ClientSession() as session:
            # Try QR Server API first (100% free, no limits)
            try:
                qr_api_url = "https://api.qrserver.com/v1/create-qr-code/"
                params = {
                    "size": "300x300",
                    "data": text_to_encode,
                    "format": "png",
                    "bgcolor": "ffffff",
                    "color": "000000",
                    "qzone": "1",
                    "margin": "10"
                }
                
                async with session.get(qr_api_url, params=params) as response:
                    if response.status == 200:
                        # Get QR code image bytes
                        qr_bytes = await response.read()
                        
                        # Create BytesIO object
                        bio = io.BytesIO(qr_bytes)
                        bio.name = f"qrcode_{user.id}_{int(datetime.now().timestamp())}.png"
                        
                        # Send QR code
                        await update.message.reply_photo(
                            photo=bio,
                            caption=f"""
📱 **QR Code généré avec succès !**

📝 **Contenu :** {text_to_encode[:100]}{'...' if len(text_to_encode) > 100 else ''}
📊 **Taille :** 300x300 pixels
🎨 **Format :** PNG haute qualité
🤖 **Généré par :** NICE-BOT via QR Server API

💡 *Scannez avec votre téléphone !*
                            """,
                            parse_mode='Markdown'
                        )
                        return
                        
            except Exception as api_error:
                logger.warning(f"QR Server API failed, trying local generation: {api_error}")
            
            # Fallback to local QR code generation
            qr_code = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_code.add_data(text_to_encode)
            qr_code.make(fit=True)
            
            # Create image
            img = qr_code.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            bio = io.BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            bio.name = 'qrcode_local.png'
            
            # Send QR code
            await update.message.reply_photo(
                photo=bio,
                caption=f"""
📱 **QR Code généré (Local)**

📝 **Contenu :** {text_to_encode[:100]}{'...' if len(text_to_encode) > 100 else ''}
🔄 **Méthode :** Génération locale de secours
💡 *Scannez avec votre téléphone !*
                """,
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"QR code generation error: {e}")
        await update.message.reply_text(
            "❌ **Erreur lors de la génération du QR code**\n\n"
            "Une erreur technique s'est produite. Réessayez plus tard.",
            parse_mode='Markdown'
        )

async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pdf command - PDF generation using local FPDF library"""
    user = update.effective_user
    
    # Log command
    db_user = get_user(str(user.id))
    if db_user:
        add_history(db_user['id'], '/pdf', ' '.join(context.args))
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage :** /pdf <texte>\n\n"
            "**Exemple :** /pdf Voici le contenu de mon PDF\n"
            "**Exemple :** /pdf Bonjour, ceci est un test de génération PDF avec NICE-BOT !\n\n"
            "💡 **Astuce :** Génération 100% locale, rapide et gratuite !",
            parse_mode='Markdown'
        )
        return
    
    text_content = ' '.join(context.args)
    
    try:
        # Send typing action
        await update.message.reply_chat_action("upload_document")
        
        # Create PDF using FPDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Document NICE-BOT", ln=True, align='C')
        pdf.ln(5)
        
        # Add metadata
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 5, f"Genere le: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
        pdf.cell(0, 5, f"Utilisateur: {user.first_name or 'N/A'}", ln=True)
        pdf.ln(10)
        
        # Add content
        pdf.set_font("Arial", size=12)
        
        # Handle long text with proper encoding
        try:
            # Try to encode in latin-1 (FPDF default)
            text_encoded = text_content.encode('latin-1', errors='replace').decode('latin-1')
        except:
            # Fallback: remove non-latin characters
            text_encoded = text_content.encode('ascii', errors='ignore').decode('ascii')
        
        # Add text with word wrap
        pdf.multi_cell(0, 10, text_encoded)
        
        # Add footer
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, "Powered by NICE-BOT - Generation locale Python", ln=True, align='C')
        
        # Generate PDF bytes (FPDF2 returns bytes directly)
        pdf_bytes = pdf.output()
        
        # Create BytesIO object
        bio = io.BytesIO(pdf_bytes)
        bio.name = f"document_{user.id}_{int(datetime.now().timestamp())}.pdf"
        bio.seek(0)
        
        # Send PDF document
        await update.message.reply_document(
            document=bio,
            caption=f"""
📄 **PDF généré avec succès !**

📝 **Contenu :** {text_content[:50]}{'...' if len(text_content) > 50 else ''}
📊 **Taille :** {len(pdf_bytes):,} bytes
🐍 **Méthode :** Génération locale Python (FPDF)
⚡ **Avantage :** 100% gratuit, rapide, sans API !

✨ *Généré localement par NICE-BOT*
            """,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        await update.message.reply_text(
            "❌ **Erreur lors de la génération du PDF**\n\n"
            f"Détails: {str(e)}\n\n"
            "Réessayez avec un texte plus court ou sans caractères spéciaux.",
            parse_mode='Markdown'
        )
