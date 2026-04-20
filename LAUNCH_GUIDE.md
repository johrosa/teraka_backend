# Guide de Lancement des Serveurs Teraka

Ce projet utilise un système de lancement unifié pour Django et PostgREST, compatible avec les environnements de développement et production.

## 📋 Prérequis

- **Python 3.8+**
- **PostgreSQL** installé et en cours d'exécution
- **PostgREST** (fourni dans `api/`)
- Base de données **teraka** créée

### Installation des dépendances Python

```bash
# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv

# Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur Linux/macOS:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Pour production, ajouter gunicorn
pip install gunicorn
```

## 🚀 Lancement

### **Option 1: Script Python (Recommandé - Multiplateforme)**

```bash
# Développement
python run_servers.py

# Production
python run_servers.py --env production

# Avec ports personnalisés
python run_servers.py --django-port 8080 --postgrest-port 3001
```

### **Option 2: Batch/Shell Scripts**

**Windows:**
```cmd
# Double-clic sur run_servers.bat
# Ou en ligne de commande:
run_servers.bat

# Production
run_servers.bat --env production
```

**Linux/macOS:**
```bash
# Donner les permissions d'exécution
chmod +x run_servers.sh

# Lancer
./run_servers.sh

# Production
./run_servers.sh --env production
```

## 🔧 Options de Lancement

```bash
usage: run_servers.py [-h] [--env {development,production}] 
                      [--django-port DJANGO_PORT] 
                      [--postgrest-port POSTGREST_PORT]

Options:
  --env {development,production}
                        Environnement d'exécution (défaut: development)
  --django-port PORT    Port Django (défaut: 8000)
  --postgrest-port PORT Port PostgREST (défaut: 3000)
```

## 📍 Accès une fois lancé

- **Django Admin**: http://localhost:8000/admin/
- **Login API**: http://localhost:8000/api/login/
- **PostgREST**: http://localhost:3000

## 🛑 Arrêt des Serveurs

Pressez **Ctrl+C** dans le terminal. Les serveurs s'arrêteront proprement.

## ⚙️ Configuration Production

Pour la production, assurez-vous que:

1. **Django DEBUG = False** dans `config/settings.py`
2. **ALLOWED_HOSTS** contient votre domaine
3. **STATIC_ROOT** est configuré
4. **SECRET_KEY** est définie via variables d'environnement
5. **PostgREST** utilise les bonnes credentials DB

### Variables d'environnement Production

```bash
# Linux/macOS
export DJANGO_SECRET_KEY="your-secret-key"
export DATABASE_URL="postgres://user:pass@host/db"
export DEBUG=False

# Windows (CMD)
set DJANGO_SECRET_KEY=your-secret-key
set DATABASE_URL=postgres://user:pass@host/db
set DEBUG=False

# Windows (PowerShell)
$env:DJANGO_SECRET_KEY = "your-secret-key"
```

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│         Client / Frontend                   │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼─────┐  ┌───▼────────┐
   │  Django  │  │ PostgREST  │
   │ :8000    │  │ :3000      │
   └────┬─────┘  └───┬────────┘
        │            │
        └────┬───────┘
             │
        ┌────▼────────┐
        │ PostgreSQL  │
        │  (Teraka DB)│
        └─────────────┘
```

## 🐛 Dépannage

### PostgREST ne démarre pas
- Vérifier que PostgreSQL est en cours d'exécution
- Vérifier la configuration `api/postgrest.conf`
- Tester la connexion DB: `psql postgres://user:pass@localhost/teraka`

### Django ne démarre pas
- Vérifier que le port 8000 n'est pas utilisé: `netstat -tuln | grep 8000` (Linux)
- Vérifier les migrations: `python manage.py migrate`
- Vérifier les logs Django

### Port déjà utilisé
```bash
# Windows - Trouver le processus qui utilise le port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux - Tuer le processus sur le port 8000
lsof -ti:8000 | xargs kill -9
```

## 📦 Déploiement Systématique

Pour un déploiement de production robuste:

```bash
# 1. Collectionner les fichiers statiques
python manage.py collectstatic --noinput

# 2. Appliquer les migrations
python manage.py migrate

# 3. Lancer en production
python run_servers.py --env production
```

Ou utiliser un gestionnaire de processus comme:
- **systemd** (Linux)
- **supervisor** (Linux/Windows)
- **Docker** (tout OS)

## 📝 Logs

Les logs sont affichés en temps réel dans le terminal. Pour les logs persistants en production:

```python
# Dans config/settings.py, configurer LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/teraka/django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```
