# 🛠️ Guide de Dépannage - Teraka Platform

## Les processus s'arrêtent immédiatement au démarrage

### Diagnostic

D'abord, lancez le script de diagnostic:

```bash
python diagnose.py
```

Ce script vérifiera tous les prérequis et vous indiquera ce qui manque.

### Causes Communes

#### 1. **PostgreSQL n'est pas accessible**

```
❌ PostgreSQL non accessible: connection refused
```

**Solutions:**
```bash
# Windows - Vérifier que PostgreSQL est en cours d'exécution
# Services Windows → "PostgreSQL" → Démarrer

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql

# Tester la connexion
psql -h localhost -U postgres -d teraka
```

#### 2. **La base de données 'teraka' n'existe pas**

```
❌ PostgreSQL non accessible: FATAL: database "teraka" does not exist
```

**Solution:**
```bash
# Créer la base de données
psql -U postgres -c "CREATE DATABASE teraka;"

# Avec PostGIS (recommandé pour ce projet)
psql -U postgres -c "CREATE DATABASE teraka TEMPLATE template1;"
psql -d teraka -U postgres -c "CREATE EXTENSION postgis;"
```

#### 3. **Credentials PostgreSQL incorrectes**

Vérifiez les identifiants dans `api/postgrest.conf`:

```conf
db-uri = "postgres://postgres:ad,in@localhost:5432/teraka"
```

**Changer le mot de passe:**
```bash
# Réinitialiser le mot de passe PostgreSQL
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'new_password';"

# Puis mettre à jour api/postgrest.conf
```

#### 4. **PostgREST exécutable manquant ou incorrect**

```
❌ PostgREST exécutable non trouvé
```

**Solution:**
- Vérifier que `api/postgrest.exe` existe (Windows) ou `api/postgrest` (Linux/macOS)
- Télécharger PostgREST depuis https://postgrest.org/en/stable/installation.html
- Placer l'exécutable dans le répertoire `api/`

#### 5. **Django ne trouve pas ses dépendances**

```
ModuleNotFoundError: No module named 'django'
```

**Solution:**
```bash
# Réinstaller les dépendances
pip install -r requirements.txt

# Si requirements.txt n'existe pas, créez-le:
pip freeze > requirements.txt
```

#### 6. **Port déjà utilisé**

```
[Errno 48] Address already in use
```

**Solution:**
```bash
# Windows - Trouver le processus sur le port 8000
netstat -ano | findstr :8000
# Résultat: TCP    127.0.0.1:8000    0.0.0.0:0      LISTENING    1234
# Tuer le processus
taskkill /PID 1234 /F

# Linux
lsof -ti:8000 | xargs kill -9

# macOS
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# OU utiliser un port différent
python run_servers.py --django-port 8080 --postgrest-port 3001
```

---

## Les serveurs démarrent mais ne répondent pas

### 1. **Vérifier qu'ils tournent réellement**

```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux
netstat -tuln | grep -E "8000|3000"

# macOS
lsof -i :8000
lsof -i :3000
```

### 2. **Vérifier les logs**

Les logs s'affichent en temps réel dans le terminal. Cherchez les messages d'erreur.

### 3. **Testez les endpoints**

```bash
# Django
curl http://localhost:8000/admin/

# PostgREST
curl http://localhost:3000

# API Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

---

## Erreurs Spécifiques

### `django.db.utils.ProgrammingError: relation "table_name" does not exist`

**Solution:**
```bash
# Exécuter les migrations
python manage.py migrate

# Ou créer les tables à partir du schéma
python manage.py inspectdb > core/models_new.py
```

### `CORS error` du frontend

Vérifier que CORS est configuré correctement dans `config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # Frontend dev
    "http://localhost:3001",
    "https://yourdomain.com",   # Production
]
```

### `psycopg2.OperationalError: could not connect to server`

PostgreSQL n'est pas accessible. Vérifications:

```bash
# 1. PostgreSQL tourne?
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql

# 2. Port correct?
# Par défaut: 5432
netstat -tuln | grep 5432

# 3. Firewall?
# Assurez-vous que le port 5432 est accessible

# 4. Host correct?
# postgresql.conf → listen_addresses = '*'
```

### `jwt-secret mismatch`

Les secrets JWT doivent être identiques entre Django et PostgREST:

**Django** (`config/settings.py`):
```python
SECRET_KEY = 'django-insecure-3=#-gb(y!sq*&=2chy@7k#+0&-uv2#w%+v4!anm#u(=&g@797^'
```

**PostgREST** (`api/postgrest.conf`):
```conf
jwt-secret = "django-insecure-3=#-gb(y!sq*&=2chy@7k#+0&-uv2#w%+v4!anm#u(=&g@797^"
```

---

## Collecte d'Informations pour le Support

Si vous ne pouvez pas résoudre le problème, collectez ces informations:

```bash
# 1. Diagnostic complet
python diagnose.py > diagnostic.txt

# 2. Version des outils
python --version
psql --version

# 3. Logs du démarrage
python run_servers.py > startup.log 2>&1
# Pressez Ctrl+C après quelques secondes

# 4. Statut des ports
# Windows
netstat -ano > ports.txt

# Linux/macOS
netstat -tuln > ports.txt
lsof -i > ports.txt

# Partagez tous ces fichiers .txt
```

---

## Configuration Recommandée pour Production

### 1. **Variables d'environnement**

Créer un fichier `.env`:
```bash
cp .env.example .env
# Éditer .env avec les values production
```

### 2. **Sécurité**

```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')  # En variables d'env!
```

### 3. **Base de données distante**

```conf
# api/postgrest.conf
db-uri = "postgres://user:password@db.example.com:5432/teraka"
```

### 4. **SSL/TLS**

```python
# config/settings.py en production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Utile: Commandes Django Courantes

```bash
# Migrations
python manage.py migrate
python manage.py makemigrations

# Créer un superutilisateur
python manage.py createsuperuser

# Importer des données QGIS
python manage.py import_qgis_data --path data.geojson

# Shell interactif
python manage.py shell

# Tests
python manage.py test
```

---

## Support

Si vous avez besoin d'aide:
1. Lancez `python diagnose.py` et partagez le résultat
2. Vérifiez les logs ci-dessus
3. Consultez la documentation:
   - Django: https://docs.djangoproject.com/
   - PostgREST: https://postgrest.org/
   - PostgreSQL: https://www.postgresql.org/docs/
