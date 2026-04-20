# 🚀 Guide d'intégration des API de Gestion

## Démarrage rapide

### 1. **Lancer les serveurs**
```bash
cd backend_django
python run_servers.py
```

### 2. **Obtenir un token JWT**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_l2",
    "password": "test123"
  }'
```

Réponse:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "Admin_L2"
}
```

### 3. **Utiliser le token pour les requêtes**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/statistics/
```

---

## 📱 Exemple d'intégration Frontend

### **React/Vue avec Axios**

#### 1. Service API
```javascript
// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// Intercepteur pour ajouter le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const managementApi = {
  // Statistiques
  getStatistics: () => api.get('/statistics/'),
  getBosquetStats: () => api.get('/bosquet-statistics/'),
  getMembersByRegion: () => api.get('/members-by-region/'),
  
  // Validation & Health
  validateData: () => api.get('/data-validation/'),
  getSystemHealth: () => api.get('/system-health/'),
  
  // Quality & Activity
  getDataQuality: () => api.get('/data-quality/'),
  getUserActivity: () => api.get('/user-activity/'),
  
  // Export
  exportData: (format, tables) => api.post('/export/', {
    format,
    tables
  })
};

export default api;
```

#### 2. Component Dashboard
```jsx
// components/AdminDashboard.jsx
import React, { useEffect, useState } from 'react';
import { managementApi } from '../services/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      const [statsRes, healthRes, qualityRes] = await Promise.all([
        managementApi.getStatistics(),
        managementApi.getSystemHealth(),
        managementApi.getDataQuality()
      ]);

      setStats(statsRes.data);
      setHealth(healthRes.data);
      setQuality(qualityRes.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur de chargement');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Chargement...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard">
      <h1>📊 Dashboard Administration</h1>

      {/* Statistiques globales */}
      <section className="stats-grid">
        <div className="stat-card">
          <h3>Communes</h3>
          <p className="stat-value">{stats?.platform?.total_communes}</p>
        </div>
        <div className="stat-card">
          <h3>Bosquets</h3>
          <p className="stat-value">{stats?.platform?.total_bosquets}</p>
        </div>
        <div className="stat-card">
          <h3>Arbres</h3>
          <p className="stat-value">{stats?.platform?.total_arbres}</p>
        </div>
        <div className="stat-card">
          <h3>Membres</h3>
          <p className="stat-value">{stats?.platform?.total_membres}</p>
        </div>
      </section>

      {/* Santé du système */}
      <section className="system-health">
        <h2>🏥 Santé du système</h2>
        <div className="health-status">
          <div className={`check ${health?.checks?.database?.status}`}>
            <strong>Base de données:</strong> {health?.checks?.database?.status}
          </div>
          <div className={`check ${health?.checks?.disk_space?.status}`}>
            <strong>Disque:</strong> {health?.checks?.disk_space?.percent_used?.toFixed(1)}% utilisé
          </div>
          <div className={`check ${health?.checks?.static_files?.status}`}>
            <strong>Fichiers statiques:</strong> {health?.checks?.static_files?.status}
          </div>
        </div>
      </section>

      {/* Qualité des données */}
      <section className="data-quality">
        <h2>📈 Qualité des données</h2>
        <div className="quality-score">
          <div className={`score ${quality?.quality_score > 70 ? 'good' : 'warning'}`}>
            {quality?.quality_score}/100
          </div>
          <div className="completeness">
            <p>Coverage bosquets: {quality?.data_completeness?.bosquets?.coverage_percent?.toFixed(1)}%</p>
            <p>Mises à jour (7j): {quality?.data_freshness?.bosquet_suivi_last_7d}</p>
          </div>
        </div>
      </section>

      <button onClick={loadDashboard}>Rafraîchir</button>
    </div>
  );
}
```

#### 3. CSS Styling
```css
/* styles/dashboard.css */
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 2.5em;
  font-weight: bold;
  color: #3498db;
  margin: 10px 0 0 0;
}

.health-status, .quality-score {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin: 20px 0;
}

.check {
  padding: 10px;
  margin: 5px 0;
  border-radius: 4px;
  border-left: 4px solid #ccc;
}

.check.ok {
  background: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.check.warning {
  background: #fff3cd;
  border-color: #ffc107;
  color: #856404;
}

.check.error {
  background: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.score.good {
  color: #28a745;
  font-size: 3em;
  font-weight: bold;
}

.score.warning {
  color: #ffc107;
  font-size: 3em;
  font-weight: bold;
}
```

---

## 🔍 Validation des Données

```javascript
// components/DataValidation.jsx
import React, { useState } from 'react';
import { managementApi } from '../services/api';

export default function DataValidation() {
  const [validation, setValidation] = useState(null);
  const [checking, setChecking] = useState(false);

  async function checkData() {
    try {
      setChecking(true);
      const res = await managementApi.validateData();
      setValidation(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setChecking(false);
    }
  }

  return (
    <div>
      <button onClick={checkData} disabled={checking}>
        {checking ? 'Vérification...' : 'Valider les données'}
      </button>

      {validation && (
        <div className="validation-results">
          <h3>Résultats de validation</h3>
          
          {validation.summary.critical && (
            <div className="alert alert-danger">
              ⚠️ {validation.summary.total_errors} erreur(s) critique(s) détectée(s)
            </div>
          )}

          {validation.errors.length > 0 && (
            <div className="errors">
              <h4>🔴 Erreurs</h4>
              {validation.errors.map((err, i) => (
                <p key={i}>{err.type}: {err.message}</p>
              ))}
            </div>
          )}

          {validation.warnings.length > 0 && (
            <div className="warnings">
              <h4>🟡 Avertissements</h4>
              {validation.warnings.map((warn, i) => (
                <p key={i}>{warn.type}: {warn.message}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 📊 Rapport d'Activité

```javascript
// components/ActivityLog.jsx
import React, { useEffect, useState } from 'react';
import { managementApi } from '../services/api';

export default function ActivityLog() {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    managementApi.getUserActivity()
      .then(res => setActivities(res.data.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>📋 Dernière activité (30 jours)</h2>
      <table>
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Action</th>
            <th>Modèle</th>
            <th>Date/Heure</th>
          </tr>
        </thead>
        <tbody>
          {activities.map((log, i) => (
            <tr key={i}>
              <td>{log.username}</td>
              <td>
                <span className={`action ${log.action}`}>
                  {log.action}
                </span>
              </td>
              <td>{log.model}</td>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 💾 Export de Données

```javascript
// components/DataExport.jsx
import React, { useState } from 'react';
import { managementApi } from '../services/api';

export default function DataExport() {
  const [exporting, setExporting] = useState(false);

  async function exportToJSON() {
    try {
      setExporting(true);
      const res = await managementApi.exportData('json', [
        'bosquets',
        'arbres',
        'membres'
      ]);

      // Télécharger le fichier
      const dataStr = JSON.stringify(res.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `export_${new Date().toISOString()}.json`;
      link.click();
    } catch (err) {
      console.error(err);
    } finally {
      setExporting(false);
    }
  }

  return (
    <button onClick={exportToJSON} disabled={exporting}>
      {exporting ? 'Exportation...' : '📥 Exporter les données'}
    </button>
  );
}
```

---

## 🧪 Tests avec cURL

```bash
# 1. Login et récupérer le token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_l2","password":"test123"}' | jq -r '.access')

# 2. Tester les endpoints
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/statistics/ | jq

# 3. Validation des données
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-validation/ | jq

# 4. Santé du système
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/system-health/ | jq

# 5. Export de données
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format":"json","tables":["bosquets"]}' \
  http://localhost:8000/api/export/ | jq
```

---

## 🚀 Déploiement en Production

### Variables d'environnement requises:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@host:5432/db
POSTGREST_DB_URI=postgres://user:pass@host:5432/db
```

### Docker:
```bash
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## 📝 Checklist d'intégration

- [ ] Django en cours d'exécution
- [ ] Token JWT obtenu
- [ ] Endpoints testés avec cURL
- [ ] Frontend intégré (React/Vue)
- [ ] Authentification JWT configurée
- [ ] Dashboard admin opérationnel
- [ ] Logs d'activité tracés
- [ ] Export de données fonctionnel
- [ ] Monitoring configuré
- [ ] Alertes mises en place

---

**Version:** 1.0  
**Date:** 2026-04-20  
**Auteur:** Teraka Platform Team
