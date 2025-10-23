# 🔒 GUIDE DE SÉCURITÉ - NICE-BOT

## ⚠️ IMPORTANT - À LIRE AVANT LE DÉPLOIEMENT

### 🚨 Informations sensibles

**NE JAMAIS** commiter ou partager publiquement :

1. **Fichier `.env`** - Contient vos clés API réelles
2. **BOT_TOKEN** - Token de votre bot Telegram
3. **ADMIN_USER_ID** - Votre ID Telegram personnel
4. **Clés API** - TMDB, Mediastack, etc.
5. **Base de données** - `data/bot.db` avec données utilisateurs

### ✅ Bonnes pratiques

#### 1. Fichier .env
```bash
# ✅ BON - Utiliser .env (ignoré par git)
BOT_TOKEN=votre_vrai_token_ici

# ❌ MAUVAIS - Ne jamais mettre dans .env.example
BOT_TOKEN=8344285611:AAGdUbpKPPOVIubNkgDJU_ek-n6OjZNbERQ
```

#### 2. .gitignore
Assurez-vous que `.gitignore` contient :
```
.env
data/bot.db
*.db
__pycache__/
.venv/
```

#### 3. Variables d'environnement sur Render
- Configurez toutes les variables dans le dashboard Render
- Ne les mettez jamais dans le code source
- Utilisez des valeurs différentes pour dev/prod

#### 4. Admin User ID
```python
# ✅ BON - Vérifier l'admin
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")

def is_admin(user_id: int) -> bool:
    return str(user_id) == str(ADMIN_USER_ID)

# ❌ MAUVAIS - ID en dur dans le code
ADMIN_USER_ID = "7662189057"
```

### 🔐 Sécurité des APIs

#### APIs avec clés
- **TMDB** : Quota 1000 requêtes/jour
- **Mediastack** : Quota 1000 requêtes/mois
- Surveillez votre usage pour éviter les dépassements

#### APIs sans clé (gratuites)
- LibreTranslate
- Open-Meteo
- ExchangeRate.host
- Wikipedia
- Quotable
- JokeAPI

### 🛡️ Protection des données utilisateurs

#### Base de données
```python
# ✅ BON - Données minimales
users table:
  - telegram_id (nécessaire)
  - username (optionnel)
  - first_name (optionnel)
  - language (préférence)
  - joined_at (timestamp)

# ❌ MAUVAIS - Ne jamais stocker
  - Numéros de téléphone
  - Emails personnels
  - Mots de passe
  - Données bancaires
```

#### Logs
```python
# ✅ BON - Logs anonymisés
logger.info(f"Command /start executed by user {user_id}")

# ❌ MAUVAIS - Logs avec données sensibles
logger.info(f"User {username} with phone {phone} executed /start")
```

### 🚀 Checklist avant déploiement

- [ ] `.env` contient vos vraies clés (pas dans git)
- [ ] `.env.example` ne contient QUE des exemples
- [ ] `.gitignore` est configuré correctement
- [ ] `ADMIN_USER_ID` est votre vrai ID Telegram
- [ ] Aucun token/clé en dur dans le code
- [ ] Base de données `bot.db` n'est pas dans git
- [ ] Variables d'environnement configurées sur Render
- [ ] Webhook Telegram pointe vers votre URL Render

### 🔍 Vérification rapide

Exécutez ces commandes pour vérifier :

```bash
# Vérifier qu'aucun secret n'est dans git
git grep -i "bot_token"
git grep -i "api_key"

# Vérifier .gitignore
cat .gitignore | grep ".env"
cat .gitignore | grep "*.db"

# Lancer le script de vérification
python check_deployment.py
```

### 📞 En cas de fuite de données

Si vous avez accidentellement exposé un token ou une clé :

1. **Bot Token** : 
   - Aller sur @BotFather
   - `/revoke` pour révoquer le token
   - Générer un nouveau token
   - Mettre à jour `.env` et Render

2. **Clés API** :
   - Se connecter au service (TMDB, Mediastack)
   - Révoquer l'ancienne clé
   - Générer une nouvelle clé
   - Mettre à jour `.env` et Render

3. **Repository Git** :
   - Supprimer le commit avec les données sensibles
   - Utiliser `git filter-branch` ou BFG Repo-Cleaner
   - Force push le repository nettoyé

### 📚 Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Telegram Bot Security](https://core.telegram.org/bots/faq#security)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**🔒 La sécurité est la responsabilité de tous !**
