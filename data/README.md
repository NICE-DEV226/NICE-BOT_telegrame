# 📁 Dossier Data - NICE-BOT

Ce dossier contient les bases de données locales utilisées par le bot pour fonctionner **sans dépendance API externe**.

## 📚 Fichiers

### `citations.json`
**Commande:** `/citation`  
**Contenu:** 50 citations inspirantes en français  
**Format:**
```json
[
  {
    "quote": "La citation...",
    "author": "Auteur"
  }
]
```

**Avantages:**
- ✅ Fonctionne offline
- ✅ Pas de limite de requêtes
- ✅ Réponse instantanée
- ✅ 100% gratuit

### `blagues.json`
**Commande:** `/blague`  
**Contenu:** 80+ blagues françaises  
**Format:**
```json
[
  "Blague 1...",
  "Blague 2...",
  ...
]
```

**Avantages:**
- ✅ Contenu en français
- ✅ Pas de dépendance API
- ✅ Facile à enrichir
- ✅ Contrôle total du contenu

### `bot.db`
**Type:** SQLite Database  
**Contenu:** 
- Utilisateurs du bot
- Historique des commandes
- Statistiques de gamification
- Badges et achievements

## 🔧 Maintenance

### Ajouter des citations
1. Ouvrir `citations.json`
2. Ajouter un objet avec `quote` et `author`
3. Redémarrer le bot

### Ajouter des blagues
1. Ouvrir `blagues.json`
2. Ajouter une nouvelle blague dans le tableau
3. Redémarrer le bot

## 📊 Statistiques

| Fichier | Taille | Nombre d'entrées |
|---------|--------|------------------|
| citations.json | ~8 KB | 50 citations |
| blagues.json | ~6 KB | 80+ blagues |
| bot.db | Variable | Données utilisateurs |

## 🚀 Avantages de l'approche locale

1. **Performance** - Réponse instantanée, pas de latence réseau
2. **Fiabilité** - Pas de dépendance à des services externes
3. **Coût** - 100% gratuit, pas de quotas
4. **Contrôle** - Contenu entièrement personnalisable
5. **Offline** - Fonctionne même sans connexion internet (pour ces commandes)

## 🔄 Mise à jour

Les fichiers JSON peuvent être mis à jour à chaud. Le bot rechargera automatiquement les données au prochain démarrage.

---

*Généré pour NICE-BOT - Python Native Optimization*
