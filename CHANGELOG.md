# 📝 CHANGELOG - NICE-BOT

## Version 2.1.0 (23 Octobre 2025)

### 🚀 Nouvelles fonctionnalités

#### Intelligence Artificielle améliorée
- ✅ **Migration vers PrinceTech GPT API** - Remplacement de HuggingFace
  - `/ai` - Réponses IA plus rapides et fiables
  - `/resume` - Résumés de texte améliorés
  - `/idee` - Génération d'idées créatives optimisée
  - API gratuite et illimitée
  - Temps de réponse considérablement réduit

#### Actualités améliorées
- ✅ **Migration vers PrinceTech Wikimedia** - Remplacement de Mediastack
  - `/news <sujet>` - Recherche d'actualités par sujet
  - Informations détaillées et à jour
  - API gratuite et illimitée
  - Plus flexible que l'ancien système

#### Menu modernisé
- ✅ **Unification des menus** - `/menu` et `/imenu` identiques
  - Suppression de l'ancien menu texte
  - Menu interactif avec boutons uniquement
  - Image intégrée en caption (menu.png)
  - Interface moderne et cohérente
  - Meilleure expérience utilisateur

#### Chatbot IA intelligent
- ✅ **Nouvelle commande `/chatbot`** - Chatbot IA conversationnel
  - Activation/désactivation par utilisateur (privé) ou admin (groupe)
  - Réponse automatique à TOUS les messages en privé
  - Réponse aux mentions et replies en groupe
  - Mémoire de conversation (20 derniers messages)
  - Réponses naturelles avec PrinceTech GPT
  - Délai aléatoire pour simuler un humain
  - Stockage persistant des paramètres

#### Traduction avancée
- ✅ **Amélioration majeure de `/traduire`**
  - Support des réponses (reply) aux messages
  - 4 APIs de traduction en cascade
  - 12 langues supportées
  - Détection automatique de langue
  - Google Translate, MyMemory, PopCat, LibreTranslate

#### Téléchargements multimédias
- ✅ **6 nouvelles commandes de téléchargement**
  - `/tiktok` - Télécharger vidéos TikTok
  - `/facebook` - Télécharger vidéos Facebook/Reels
  - `/instagram` - Télécharger reels et vidéos Instagram
  - `/twitter` - Télécharger vidéos Twitter/X
  - `/pinterest` - Télécharger vidéos Pinterest
  - `/apk` - Télécharger fichiers APK (WhatsApp, Instagram, etc.)
  - Format ASCII élégant pour les réponses
  - Téléchargement direct dans Telegram

### 🔧 Corrections de bugs

#### PDF Generation
- ✅ **Correction erreur bytearray** dans `/pdf`
  - Problème: `'bytearray' object has no attribute 'encode'`
  - Solution: Utilisation correcte de `pdf.output()` avec FPDF2
  - La génération PDF fonctionne maintenant parfaitement

#### Base de données
- ✅ **Ajout fonction manquante** `get_recent_history()` dans `db.py`
- ✅ **Correction imports** dans `admin.py` - Ajout de `get_connection`

#### Messages d'administration
- ✅ **Amélioration messages d'accès refusé** pour commandes admin
  - Message professionnel et informatif
  - Affichage de l'ID Telegram de l'utilisateur
  - Redirection vers /help pour les utilisateurs standards
  - Fonction générique `send_access_denied()` pour cohérence

### 🔒 Sécurité

- ✅ **Protection des tokens** dans `.env.example`
  - Suppression du vrai BOT_TOKEN exposé
  - Suppression de l'ADMIN_USER_ID exposé
  - Fichier sécurisé pour partage public

- ✅ **Création `.gitignore`**
  - Protection `.env`
  - Protection `*.db`
  - Protection `__pycache__/`
  - Protection `.venv/`

### 📚 Documentation

- ✅ **README.md mis à jour**
  - Ajout commandes gamification
  - Ajout commandes notifications
  - Ajout commandes interactives
  - Mise à jour structure du projet
  - Mise à jour tableau des APIs

- ✅ **Nouveaux fichiers créés**
  - `SECURITY.md` - Guide de sécurité complet
  - `check_deployment.py` - Script de vérification
  - `CHANGELOG.md` - Ce fichier
  - `.gitignore` - Protection fichiers sensibles

### 🎯 APIs utilisées

**Nouvelles APIs:**
- PrinceTech GPT API (IA)
- PrinceTech Wikimedia (actualités)
- QR Server API (QR codes)
- Reddit Meme API (memes)
- PopCat API (traduction fallback)

**APIs conservées:**
- LibreTranslate (traduction)
- PrinceTech Weather (météo principale)
- Open-Meteo (météo fallback)
- ExchangeRate.host (devises)
- TMDB (films)
- Wikipedia (encyclopédie)
- Quotable (citations)
- JokeAPI (blagues)

**APIs retirées:**
- HuggingFace (remplacée par PrinceTech GPT)
- Mediastack (remplacée par PrinceTech Wikimedia)

### 📊 Statistiques

- **35+ commandes** disponibles
- **12 APIs gratuites** intégrées
- **5 tables** de base de données
- **9 modules** de commandes
- **100% gratuit** et open-source

---

## Version 2.0.0 (Précédent)

### Fonctionnalités principales
- Système de gamification (XP, niveaux, badges)
- Menus interactifs avec boutons
- Système de notifications et rappels
- Panel d'administration complet
- Base de données SQLite étendue
- Support multi-commandes

---

## Version 1.0.0 (Initial)

### Première version
- Commandes de base (start, help, menu, about)
- Utilitaires (traduction, météo, devises, QR, PDF)
- IA basique (HuggingFace)
- Info/Fun (citations, blagues, films, news, wiki)
- Commandes dev (ping, uptime, logs)
- Base de données SQLite simple
- Déploiement sur Render

---

**Développé avec ❤️ par NICE-DEV**
