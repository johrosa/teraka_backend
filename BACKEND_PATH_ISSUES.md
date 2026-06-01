# Backend File Location & Path Portability Issues

**Date**: June 1, 2026  
**Branch**: `fix/file-location-accessibility`

## 🔴 Issues in Backend

### 1. Docker Compose Hardcoded Paths ❌

**File**: `docker-compose.prod.yml`

**Current**:
```yaml
volumes:
  - ./:/app                    # Relative (OK)
  - ./logs:/app/logs          # Relative (OK)
  - ./api/postgrest.conf:/etc/postgrest/postgrest.conf:ro  # Relative (OK)
```

**But** — when run from different directory or Docker Desktop on Mac/Win:
- D: drive references don't work in Docker containers
- Paths need to be absolute or properly mapped

### 2. Run Servers Script Paths ❌

**File**: `run_servers.py`

**Current**:
```python
PROJECT_DIR = Path(__file__).resolve().parent  # ✅ OK
DJANGO_DIR = PROJECT_DIR  # ✅ OK
...
postgrest_exe = DJANGO_DIR / "api" / ("postgrest.exe" if self.is_windows else "postgrest")
```

**But** — environment-specific:
- Windows assumes postgrest.exe in `api/` folder
- No env var override for paths
- CI/CD cannot customize paths

### 3. PostgreSQL Connection String ❌

**File**: `api/postgrest.conf`

**Current**:
```
db-uri = "postgres://postgres:admin@postgres:5432/teraka"
server-host = "0.0.0.0"
server-port = 3000
```

**Issues**:
- Hardcoded password (should use env vars or secrets)
- Docker network reference `postgres` — OK, but not portable to raw Postgres
- Port hardcoded

---

## ✅ Solutions for Backend

### Solution 1: Use `.env` File for Environment Variables

**Create**: `.env.example` (checked into repo)

```bash
# Database
DB_USER=postgres
DB_PASSWORD=admin
DB_NAME=teraka
DB_PORT=5432

# Django
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgREST
POSTGREST_PORT=3000
POSTGREST_SERVER_HOST=0.0.0.0

# Paths (optional, for override)
PROJECT_DIR=/app
POSTGREST_CONF_PATH=/etc/postgrest/postgrest.conf

# API
API_TIMEOUT=30
```

**Usage**:
```bash
# Load automatically (if file exists)
docker compose --env-file .env.prod -f docker-compose.prod.yml up

# Or set manually
export DB_PASSWORD=secure_password
docker compose ... up
```

### Solution 2: Update `docker-compose.prod.yml` for Portability

**Before**:
```yaml
postgrest:
  image: postgrest/postgrest:latest
  volumes:
    - ./api/postgrest.conf:/etc/postgrest/postgrest.conf:ro
```

**After**:
```yaml
postgrest:
  image: postgrest/postgrest:latest
  environment:
    PGRST_DB_URI: postgres://${DB_USER:-postgres}:${DB_PASSWORD:-admin}@postgres:${DB_PORT:-5432}/${DB_NAME:-teraka}
    PGRST_DB_SCHEMA: ${DB_SCHEMA:-public}
    PGRST_SERVER_HOST: ${POSTGREST_SERVER_HOST:-0.0.0.0}
    PGRST_SERVER_PORT: ${POSTGREST_PORT:-3000}
  # Optional: if still using config file
  # volumes:
  #   - ${POSTGREST_CONF_PATH:-.}/api/postgrest.conf:/etc/postgrest/postgrest.conf:ro
```

### Solution 3: Update `run_servers.py` for Cross-Platform

**Before**:
```python
PROJECT_DIR = Path(__file__).resolve().parent
DJANGO_DIR = PROJECT_DIR
postgrest_exe = DJANGO_DIR / "api" / ("postgrest.exe" if self.is_windows else "postgrest")
```

**After**:
```python
# Get project dir from env or use script directory
PROJECT_DIR = Path(os.getenv('TERAKA_PROJECT_DIR', __file__)).resolve().parent
DJANGO_DIR = PROJECT_DIR

# Allow override postgrest path
postgrest_exe = Path(os.getenv('POSTGREST_BIN', DJANGO_DIR / "api" / ("postgrest.exe" if self.is_windows else "postgrest")))

# Database connection with env override
db_uri = os.getenv('DATABASE_URL', "postgres://postgres:admin@localhost:5432/teraka")
```

### Solution 4: Create Setup Script

**Create**: `setup.sh` (Linux/Mac)

```bash
#!/bin/bash
# Initialize project with proper directory structure

mkdir -p logs media staticfiles
cp .env.example .env

echo "✓ Project initialized. Edit .env with your settings."
echo "  Then run: docker compose -f docker-compose.prod.yml up --build"
```

**Create**: `setup.ps1` (Windows)

```powershell
# PowerShell version
New-Item -Type Directory -Force logs, media, staticfiles
Copy-Item .env.example .env

Write-Host "✓ Project initialized. Edit .env with your settings."
```

### Solution 5: Document Environment Variables

**Create**: `ENVIRONMENT_VARIABLES.md`

```markdown
# Environment Variables Reference

## Database
- `DB_USER` — PostgreSQL user (default: postgres)
- `DB_PASSWORD` — PostgreSQL password (default: admin)
- `DB_NAME` — Database name (default: teraka)
- `DB_PORT` — PostgreSQL port (default: 5432)
- `DATABASE_URL` — Full connection string (overrides DB_* vars)

## Django
- `DJANGO_SECRET_KEY` — Secret key for Django (required for production)
- `DJANGO_DEBUG` — Debug mode (False for production)
- `ALLOWED_HOSTS` — Comma-separated list

## PostgREST
- `POSTGREST_PORT` — Port (default: 3000)
- `POSTGREST_SERVER_HOST` — Bind address (default: 0.0.0.0)
- `POSTGREST_CONF_PATH` — Custom config file path

## Paths
- `TERAKA_PROJECT_DIR` — Override project directory
- `POSTGREST_BIN` — Path to postgrest executable

## Other
- `API_TIMEOUT` — HTTP timeout in seconds (default: 30)
```

---

## 📋 Implementation Checklist

- [ ] Create `.env.example` with all variables
- [ ] Update `docker-compose.prod.yml` to use env vars
- [ ] Update `run_servers.py` to support `TERAKA_PROJECT_DIR` env var
- [ ] Create `setup.sh` and `setup.ps1` scripts
- [ ] Create `ENVIRONMENT_VARIABLES.md` documentation
- [ ] Update `README.md` with env var section
- [ ] Add `.env` to `.gitignore` (never commit secrets)
- [ ] Test on Linux/Mac paths

---

## Status

**Branch**: `fix/file-location-accessibility`  
**Created**: 2026-06-01 16:35  
**Next**: Implement environment variable support
