# 🤖 NICE-BOT

Un chatbot Telegram polyvalent et moderne, hébergé gratuitement avec des fonctionnalités utiles pour tous.

## ✨ Fonctionnalités

### 🧭 Commandes générales
- `/start` - Message de bienvenue et enregistrement
- `/help` - Aide rapide
- `/menu` ou `/imenu` - Menu interactif avec boutons et image
- `/quick` - Actions rapides avec clavier personnalisé
- `/about` - Informations sur le bot

### 🧰 Utilitaires
- `/traduire <texte>` - Traduction automatique (LibreTranslate)
- `/meteo <ville>` - Météo actuelle (Open-Meteo)
- `/devise <montant> <de> <vers>` - Conversion de devises (ExchangeRate.host)
- `/qr <texte>` - Génération de QR code
- `/pdf <texte>` - Création de PDF

### 🧠 Intelligence Artificielle
- `/ai <question>` - Réponses IA (PrinceTech GPT)
- `/resume <texte>` - Résumé automatique (PrinceTech AI)
- `/idee <sujet>` - Génération d'idées créatives (PrinceTech AI)

### 🎮 Fun & Information
- `/citation` - Citations inspirantes (Quotable)
- `/blague` - Blagues aléatoires (JokeAPI)
- `/meme` - Memes aléatoires de Reddit
- `/film <nom>` - Recherche de films (TMDB)
- `/news <sujet>` - Actualités et infos (PrinceTech Wikimedia)
- `/wiki <terme>` - Recherche Wikipédia

### 🎯 Gamification
- `/profil` - Voir votre profil XP et badges
- `/classement` - Classement des joueurs
- Système de niveaux et XP automatique
- Badges à débloquer

### 🤖 Chatbot IA
- `/chatbot on/off` - Activer/désactiver le chatbot IA
- Réponse automatique en privé (tous les messages)
- Réponse aux mentions et replies en groupe
- Mémoire de conversation intelligente

### 📥 Téléchargements
- `/tiktok <url>` - Télécharger vidéos TikTok
- `/facebook <url>` - Télécharger vidéos Facebook
- `/instagram <url>` - Télécharger reels/vidéos Instagram
- `/twitter <url>` - Télécharger vidéos Twitter/X
- `/pinterest <url>` - Télécharger vidéos Pinterest
- `/apk <nom>` - Télécharger fichiers APK

### 👥 Gestion de Groupe
- `/setup` - Configuration complète du groupe
- `/invite` - Générer liens d'invitation
- `/groupinfo` - Informations du groupe
- `/permissions` - Vérifier permissions du bot
- Message de bienvenue automatique
- Configuration par boutons interactifs

### ⏰ Notifications
- `/rappel <temps> <message>` - Programmer un rappel
- `/rappels` - Voir vos rappels actifs
- `/alertes <ville>` - Alertes météo

### 🛠️ Développement
- `/ping` - Test de connectivité
- `/uptime` - Temps de fonctionnement
- `/logs` - Logs récents (admin uniquement)

### 🛡️ Administration
- `/admin` - Panel administrateur
- `/stats` - Statistiques détaillées
- `/users` - Liste des utilisateurs
- `/broadcast` - Message à tous
- `/ban` / `/unban` - Gestion des utilisateurs
- `/addxp` / `/resetxp` - Gestion XP
- `/gamestats` - Stats gamification

## 🚀 Installation

### Prérequis
- Python 3.11+
- Compte Telegram et bot token
- Clés API gratuites (optionnelles)

### Configuration locale

1. **Cloner le projet**
```bash
git clone <repository-url>
cd NICE-BOT
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

4. **Lancer le bot**
```bash
python main.py
```

### Déploiement sur Render

1. **Connecter votre repository GitHub à Render**
2. **Créer un nouveau Web Service**
3. **Configuration :**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. **Variables d'environnement :**
   - Ajouter toutes les variables de `.env.example`
5. **Configurer le webhook Telegram :**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<your-render-url>/webhook"
```

## 🔧 APIs utilisées

| Service | API | Coût | Usage |
|---------|-----|------|-------|
| PrinceTech | Météo + IA GPT + Wikimedia | Gratuit | Illimité |
| LibreTranslate | Traduction | Gratuit | Illimité |
| PopCat | Traduction (fallback) | Gratuit | Illimité |
| Open-Meteo | Météo (fallback) | Gratuit | Illimité |
| ExchangeRate.host | Devises | Gratuit | Illimité |
| QR Server | QR Codes | Gratuit | Illimité |
| FPDF2 | PDF (local) | Gratuit | Illimité |
| TMDB | Films | Gratuit | 1000 req/jour |
| Reddit Meme API | Memes | Gratuit | Illimité |
| Quotable | Citations | Gratuit | Illimité |
| JokeAPI | Blagues | Gratuit | Illimité |
| Wikipedia | Encyclopédie | Gratuit | Illimité |

## 📁 Structure du projet

```
NICE-BOT/
├── main.py              # FastAPI webhook server
├── bot.py               # Configuration Telegram
├── db.py                # Gestion SQLite
├── commands/
│   ├── __init__.py      # Package commands
│   ├── general.py       # Commandes générales
│   ├── utils.py         # Utilitaires
│   ├── ai.py            # Intelligence artificielle
│   ├── info.py          # Info & fun
│   ├── dev.py           # Développement
│   ├── admin.py         # Administration
│   ├── interactive.py   # Menus interactifs
│   ├── gamification.py  # Système XP/badges
│   └── notifications.py # Rappels et alertes
├── assets/
│   └── menu.png         # Image du menu
├── data/
│   ├── bot.db           # Base de données SQLite
│   ├── citations.json   # Citations locales
│   └── blagues.json     # Blagues locales
├── requirements.txt     # Dépendances Python
├── .env.example         # Template variables d'environnement
├── .gitignore           # Fichiers à ignorer
├── render.yaml          # Configuration Render
├── README.md            # Documentation
└── DEPLOYMENT.md        # Guide de déploiement
```

## 🗄️ Base de données

Le bot utilise SQLite avec plusieurs tables :

- **users** : Informations des utilisateurs (telegram_id, username, first_name, language, joined_at)
- **history** : Historique des commandes (user_id, command, input, output, created_at)
- **user_stats** : Statistiques gamification (xp_points, level, total_commands, streak_days, last_activity)
- **badges** : Définition des badges (name, description, icon, xp_required, special_condition)
- **user_badges** : Badges obtenus par utilisateur (user_id, badge_id, earned_at)

## 🔒 Sécurité

- Variables d'environnement pour les clés API
- Validation des entrées utilisateur
- Logs des erreurs et activités
- Accès admin restreint pour les logs

## 📊 Monitoring

- Endpoint `/healthz` pour UptimeRobot
- Logs structurés avec timestamps
- Statistiques d'utilisation
- Monitoring des erreurs

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour signaler un bug ou demander une fonctionnalité :
1. Ouvrir une issue sur GitHub
2. Contacter l'équipe de développement
3. Utiliser la commande `/logs` (admin) pour diagnostiquer

## 🎯 Roadmap

- [ ] Support multilingue complet
- [ ] Commandes personnalisées par utilisateur
- [ ] Intégration avec plus d'APIs
- [ ] Interface web d'administration
- [ ] Système de plugins

---

**Développé avec ❤️ par l'équipe NICE**
