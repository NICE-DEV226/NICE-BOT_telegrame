# 🚀 NICE-BOT Deployment Guide

Guide complet pour déployer NICE-BOT sur Render (gratuit).

## 📋 Prérequis

### 1. Créer un bot Telegram
1. Ouvrir Telegram et chercher `@BotFather`
2. Envoyer `/newbot`
3. Suivre les instructions pour nommer votre bot
4. Copier le **token** fourni

### 2. Obtenir les clés API (optionnelles mais recommandées)

#### TMDB (Films)
1. Aller sur [themoviedb.org](https://www.themoviedb.org/)
2. Créer un compte gratuit
3. Aller dans Paramètres > API
4. Demander une clé API (gratuite)

#### Mediastack (Actualités)
1. Aller sur [mediastack.com](https://mediastack.com/)
2. S'inscrire pour un compte gratuit
3. Copier la clé API du dashboard

## 🔧 Déploiement sur Render

### Étape 1: Préparer le code
1. Fork ce repository ou upload votre code sur GitHub
2. Tester localement avec `python test_bot.py`

### Étape 2: Créer le service Render
1. Aller sur [render.com](https://render.com/)
2. Créer un compte gratuit
3. Cliquer sur "New +" → "Web Service"
4. Connecter votre repository GitHub

### Étape 3: Configuration du service
```
Name: nice-bot (ou votre choix)
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### Étape 4: Variables d'environnement
Ajouter ces variables dans l'onglet "Environment":

**Obligatoire:**
- `BOT_TOKEN`: Votre token Telegram

**Optionnelles:**
- `TMDB_API_KEY`: Clé TMDB pour /film
- `MEDIASTACK_API_KEY`: Clé Mediastack pour /news
- `ADMIN_USER_ID`: Votre ID Telegram pour /logs
- `LIBRETRANSLATE_URL`: https://libretranslate.com (défaut)

### Étape 5: Déployer
1. Cliquer sur "Create Web Service"
2. Attendre la fin du build (5-10 minutes)
3. Noter l'URL de votre service (ex: `https://nice-bot-xyz.onrender.com`)

### Étape 6: Configurer le webhook Telegram
Remplacer `<BOT_TOKEN>` et `<RENDER_URL>` par vos valeurs:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=<RENDER_URL>/webhook"
```

Exemple:
```bash
curl -X POST "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook?url=https://nice-bot-xyz.onrender.com/webhook"
```

## ✅ Vérification

### 1. Tester le service
- Aller sur `https://votre-url.onrender.com/healthz`
- Vous devriez voir: `{"status": "healthy", ...}`

### 2. Tester le bot
- Envoyer `/start` à votre bot sur Telegram
- Le bot devrait répondre avec le message de bienvenue

### 3. Monitoring
- Configurer UptimeRobot pour ping `/healthz`
- Surveiller les logs dans le dashboard Render

## 🔧 Maintenance

### Mise à jour du code
1. Push les changements sur GitHub
2. Render redéploiera automatiquement

### Surveillance
- Render Free Tier: 750h/mois (suffisant pour 24/7)
- Le service s'endort après 15min d'inactivité
- Premier ping peut prendre 30 secondes

### Logs
- Voir les logs dans le dashboard Render
- Utiliser `/logs` (admin) pour les logs applicatifs

## 🚨 Dépannage

### Bot ne répond pas
1. Vérifier que le webhook est configuré:
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

2. Vérifier les logs Render pour les erreurs

3. Tester l'endpoint:
```bash
curl https://votre-url.onrender.com/healthz
```

### Erreurs communes

**"BOT_TOKEN not found"**
- Vérifier que BOT_TOKEN est défini dans les variables d'environnement

**"Service unavailable"**
- Le service Render peut être en cours de réveil (attendre 30s)

**"Webhook already set"**
- Supprimer l'ancien webhook:
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/deleteWebhook"
```

### APIs ne fonctionnent pas
- Vérifier les clés API dans les variables d'environnement
- Certaines APIs ont des quotas (TMDB: 1000/jour)
- Le bot fonctionne même sans les APIs optionnelles

## 📊 Limites Render Free Tier

- **750 heures/mois** (suffisant pour 24/7)
- **512 MB RAM**
- **Service s'endort** après 15min d'inactivité
- **Réveil automatique** au premier ping
- **Pas de domaine personnalisé**

## 🔄 Migration vers un autre hébergeur

Le bot est compatible avec:
- **Railway** (similaire à Render)
- **Heroku** (payant)
- **VPS** (DigitalOcean, Linode, etc.)

Il suffit d'adapter les variables d'environnement et la commande de démarrage.

---

**🎉 Votre bot est maintenant en ligne 24/7 !**
