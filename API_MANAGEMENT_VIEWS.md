# API de Gestion de Plateforme Teraka

## 📋 Vue d'ensemble

Une suite complète d'APIs pour gérer et monitorer la plateforme Teraka. Toutes ces endpoints requièrent une authentification admin (JWT token avec permission admin).

---

## 🔐 Authentification

Tous les endpoints de gestion nécessitent:
1. **Token JWT valide** (voir `/api/login/`)
2. **Permissions admin** (is_staff=True et is_superuser=True)

### Format des requêtes:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/endpoint/
```

---

## 📊 Endpoints disponibles

### 1. **Statistiques Globales**
**URL:** `GET /api/statistics/`

Récupère les statistiques globales de la plateforme.

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "platform": {
    "total_communes": 15,
    "total_bosquets": 245,
    "total_arbres": 5890,
    "total_membres": 1203,
    "total_pg": 489
  },
  "suivi": {
    "bosquets_suivi": 189,
    "arbres_suivi": 3421,
    "membres_suivi": 987,
    "pg_suivi": 312
  },
  "recent_activity": {
    "bosquets_last_30d": 34,
    "arbres_last_30d": 156,
    "membres_last_30d": 78
  }
}
```

**Usage:**
```javascript
// JavaScript
const token = localStorage.getItem('access_token');
const stats = await fetch('/api/statistics/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
console.log(stats);
```

---

### 2. **Statistiques par Bosquet**
**URL:** `GET /api/bosquet-statistics/`

Affiche les statistiques détaillées pour chaque bosquet.

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "bosquets_count": 245,
  "data": [
    {
      "bosquet_id": "uuid-1234",
      "commune": "COM001",
      "suivi_count": 3
    },
    ...
  ]
}
```

---

### 3. **Validation des Données**
**URL:** `GET /api/data-validation/`

Valide l'intégrité des données et identifie les problèmes.

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "errors": [
    {
      "type": "arbres_orphelins",
      "count": 12,
      "message": "12 arbres sans bosquet"
    }
  ],
  "warnings": [
    {
      "type": "bosquets_sans_arbres",
      "count": 5,
      "message": "5 bosquets sans arbres enregistrés"
    }
  ],
  "summary": {
    "total_errors": 1,
    "total_warnings": 1,
    "critical": true
  }
}
```

**Types d'erreurs détectées:**
- ❌ Arbres orphelins (sans bosquet)
- ⚠️ Bosquets sans arbres
- ⚠️ Membres sans commune
- ⚠️ Données manquantes ou incohérentes

---

### 4. **Journal d'Activité Utilisateur**
**URL:** `GET /api/user-activity/`

Affiche les 100 dernières actions des utilisateurs (30 derniers jours).

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "logs_count": 42,
  "data": [
    {
      "username": "operateur_l1",
      "model": "bosquetsuivi",
      "action": "CREATE",
      "timestamp": "2026-04-20T09:15:00Z"
    },
    {
      "username": "admin_l1",
      "model": "userrole",
      "action": "EDIT",
      "timestamp": "2026-04-20T08:45:00Z"
    }
  ]
}
```

**Actions tracées:**
- `CREATE` - Nouvelle création
- `EDIT` - Modification
- `DELETE` - Suppression

---

### 5. **Santé du Système**
**URL:** `GET /api/system-health/`

Vérifie l'état du système (base de données, disque, fichiers).

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "status": "healthy",
  "checks": {
    "database": {
      "status": "ok",
      "message": "Base de données accessible"
    },
    "disk_space": {
      "status": "ok",
      "used_gb": 456.2,
      "total_gb": 1000.0,
      "percent_used": 45.6
    },
    "static_files": {
      "status": "ok",
      "path": "/app/static"
    }
  }
}
```

**Status possibles:**
- ✅ `ok` - Tout fonctionne
- ⚠️ `warning` - À surveiller (ex: disque > 80%)
- ❌ `error` - Problème critique

---

### 6. **Statistiques par Région**
**URL:** `GET /api/members-by-region/`

Récupère le nombre de membres par commune/région.

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "total_communes": 15,
  "data": [
    {
      "commune_code": "COM001",
      "commune_name": "Commune 1",
      "members_count": 245
    },
    {
      "commune_code": "COM002",
      "commune_name": "Commune 2",
      "members_count": 189
    }
  ]
}
```

---

### 7. **Rapport de Qualité des Données**
**URL:** `GET /api/data-quality/`

Génère un rapport complet sur la qualité et fraîcheur des données.

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "data_completeness": {
    "bosquets": {
      "baseline": 245,
      "suivi": 189,
      "coverage_percent": 77.1
    },
    "arbres": {
      "baseline": 5890,
      "suivi": 3421
    },
    "membres": {
      "total": 1203,
      "suivi": 987
    }
  },
  "data_freshness": {
    "bosquet_suivi_last_7d": 12,
    "arbre_suivi_last_7d": 56
  },
  "quality_score": 78
}
```

**Interprétation du score:**
- 90-100: Excellent
- 70-89: Bon
- 50-69: Acceptable
- < 50: Faible - Action requise

---

### 8. **Export de Données**
**URL:** `POST /api/export/`

Exporte les données au format JSON ou CSV.

**Paramètres de requête:**
```json
{
  "format": "json",
  "tables": ["bosquets", "arbres", "membres"]
}
```

**Réponse:**
```json
{
  "timestamp": "2026-04-20T10:30:00Z",
  "format": "json",
  "tables": {
    "bosquets": {
      "count": 245,
      "data": [...]
    },
    "arbres": {
      "count": 5890,
      "data": [...]
    },
    "membres": {
      "count": 1203,
      "data": [...]
    }
  }
}
```

**Exemple curl:**
```bash
curl -X POST http://localhost:8000/api/export/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "tables": ["bosquets", "arbres"]
  }'
```

---

## 🔧 Utilisation dans le Frontend

### Dashboard Admin avec React/Vue:
```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';
const token = localStorage.getItem('access_token');

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Charger les statistiques
async function loadDashboard() {
  try {
    const [stats, health, quality] = await Promise.all([
      api.get('/statistics/'),
      api.get('/system-health/'),
      api.get('/data-quality/')
    ]);
    
    console.log('Platform Statistics:', stats.data);
    console.log('System Health:', health.data);
    console.log('Data Quality:', quality.data);
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
}

// Valider les données
async function validateData() {
  const result = await api.get('/data-validation/');
  if (result.data.summary.critical) {
    console.warn('Critical data issues found:', result.data.errors);
  }
}

// Charger l'activité utilisateur
async function loadActivityLog() {
  const logs = await api.get('/user-activity/');
  console.log('Recent activities:', logs.data.data);
}
```

---

## 📈 Cas d'usage

### 1. **Monitoring en temps réel**
```bash
# Vérifier la santé du système toutes les minutes
watch -n 60 'curl -s -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/system-health/ | jq'
```

### 2. **Rapport de qualité mensuel**
```bash
# Générer un rapport et le sauvegarder
curl -s -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/data-quality/ > quality_report_$(date +%Y%m%d).json
```

### 3. **Audit d'activité**
```bash
# Surveiller les actions des utilisateurs
curl -s -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/user-activity/ | jq '.data[] | select(.action=="DELETE")'
```

### 4. **Export de données pour analyse**
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format":"json","tables":["bosquets"]}' \
  http://localhost:8000/api/export/ > export.json
```

---

## 🛡️ Sécurité

- ✅ Toutes les endpoints nécessitent authentication JWT
- ✅ Seuls les admins peuvent accéder (permission vérifiée)
- ✅ Logs d'accès tracés automatiquement
- ✅ Limites de données pour éviter surcharge (max 100 éléments par requête)

---

## 🚀 Intégration avec Monitoring

### Prometheus metrics:
```python
# À ajouter pour monitoring avancé
from prometheus_client import Counter, Histogram

api_calls = Counter('teraka_api_calls', 'API calls', ['endpoint'])
api_duration = Histogram('teraka_api_duration_seconds', 'API duration')
```

### Elasticsearch/ELK:
```bash
# Envoyer les logs vers Elasticsearch
POST /api/user-activity/ -> ELK Stack -> Kibana Dashboard
```

---

## 📞 Support

Pour des questions ou problèmes:
1. Vérifier les logs d'erreur: `tail -f /app/logs/django.log`
2. Tester l'authentification: `GET /api/login/`
3. Vérifier la santé: `GET /api/system-health/`
4. Valider les données: `GET /api/data-validation/`

---

## 📝 Changelog

**v1.0** (2026-04-20)
- ✅ Statistiques globales
- ✅ Validation des données
- ✅ Journal d'activité
- ✅ Santé du système
- ✅ Export de données
- ✅ Rapport de qualité
