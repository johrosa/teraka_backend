# Environment Variables Reference

Complete reference of all environment variables used in Teraka backend and plugin.

## Quick Start

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit with your values
nano .env   # or use your editor

# 3. Run with environment
docker compose --env-file .env -f docker-compose.prod.yml up --build
```

---

## Database Configuration

### `DB_USER`
- **Description**: PostgreSQL database user
- **Default**: `postgres`
- **Example**: `DB_USER=teraka_user`

### `DB_PASSWORD`
- **Description**: PostgreSQL password (⚠️ change in production!)
- **Default**: `admin`
- **Example**: `DB_PASSWORD=secure_password_123`
- **Security**: Never commit `.env` with real passwords

### `DB_NAME`
- **Description**: Database name
- **Default**: `teraka`
- **Example**: `DB_NAME=teraka_prod`

### `DB_PORT`
- **Description**: PostgreSQL port
- **Default**: `5432`
- **Example**: `DB_PORT=5432`

### `DB_HOST`
- **Description**: PostgreSQL host (Docker service name or IP)
- **Docker**: `postgres` (service name)
- **Local**: `localhost` or `127.0.0.1`
- **Remote**: `db.example.com`

### `DATABASE_URL` (Alternative)
- **Description**: Full connection string (overrides individual DB_* vars if set)
- **Format**: `postgres://user:password@host:port/database`
- **Example**: `DATABASE_URL=postgres://postgres:admin@postgres:5432/teraka`
- **Priority**: If set, overrides `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME`

---

## Django Configuration

### `ENV`
- **Description**: Environment type
- **Values**: `development`, `production`, `staging`
- **Default**: `production`
- **Impact**: Affects logging, security headers, gunicorn vs runserver

### `DEBUG`
- **Description**: Django debug mode
- **Values**: `True`, `False`
- **Default**: `False` (production)
- **Security**: Always `False` in production!

### `DJANGO_SECRET_KEY`
- **Description**: Django secret key for sessions/tokens
- **Default**: `django-insecure-change-me-in-production`
- **Security**: Must change in production (generate: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- **Example**: `DJANGO_SECRET_KEY=your-secret-key-here`

### `ALLOWED_HOSTS`
- **Description**: Comma-separated list of allowed hostnames
- **Default**: `localhost,127.0.0.1`
- **Example**: `ALLOWED_HOSTS=localhost,127.0.0.1,teraka.example.com`
- **Security**: Restrict to your domain in production

### `DJANGO_PORT`
- **Description**: Port for Django/Gunicorn to listen on
- **Default**: `8000`
- **Example**: `DJANGO_PORT=8000`

### `DJANGO_WORKERS`
- **Description**: Number of Gunicorn worker processes
- **Default**: `4`
- **Tuning**: `2 * CPU_cores + 1` is typical
- **Example**: `DJANGO_WORKERS=8`

### `DJANGO_TIMEOUT`
- **Description**: Gunicorn worker timeout in seconds
- **Default**: `120`
- **Tuning**: Increase for long-running requests
- **Example**: `DJANGO_TIMEOUT=300`

---

## PostgREST Configuration

### `POSTGREST_PORT`
- **Description**: Port for PostgREST API
- **Default**: `3000`
- **Example**: `POSTGREST_PORT=3000`

### `POSTGREST_SERVER_HOST`
- **Description**: Host to bind PostgREST to
- **Docker**: `0.0.0.0` (all interfaces)
- **Local**: `127.0.0.1` (localhost only)
- **Default**: `0.0.0.0`

### `POSTGREST_DB_SCHEMA`
- **Description**: PostgreSQL schema for REST API
- **Default**: `public`
- **Example**: `POSTGREST_DB_SCHEMA=public`

### `POSTGREST_DB_ANON_ROLE`
- **Description**: Anonymous user role in PostgreSQL
- **Default**: `web_anon`
- **Important**: Must match role created in database
- **Example**: `POSTGREST_DB_ANON_ROLE=web_anon`

### `POSTGREST_JWT_SECRET`
- **Description**: Secret for JWT token signing
- **Default**: `change-me-jwt-secret-at-least-32-chars`
- **Security**: Must be ≥32 chars and changed in production!
- **Example**: Generate with: `openssl rand -base64 32`

### `POSTGREST_MAX_ROWS`
- **Description**: Maximum rows returned per request (pagination)
- **Default**: `1000`
- **Impact**: Prevents large result sets from crashing API
- **Example**: `POSTGREST_MAX_ROWS=5000`

---

## API Configuration

### `POSTGREST_URL`
- **Description**: PostgREST base URL (seen by Django/plugin)
- **Docker**: `http://postgrest:3000`
- **Local Dev**: `http://localhost:3000`
- **Production**: `https://api.example.com:3001` (if exposed)
- **Example**: `POSTGREST_URL=http://postgrest:3000`

### `API_TIMEOUT`
- **Description**: HTTP request timeout in seconds
- **Default**: `30`
- **Example**: `API_TIMEOUT=60`

### `CORS_ALLOWED_ORIGINS`
- **Description**: Comma-separated list of allowed CORS origins
- **Default**: `http://localhost:3000,http://localhost:8000`
- **Example**: `CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com`
- **Security**: Restrict to your frontend domains in production

---

## Path Configuration (Advanced)

### `TERAKA_PROJECT_DIR`
- **Description**: Override project root directory
- **Default**: Detected automatically (script directory)
- **Use Case**: Running from different location
- **Example**: `TERAKA_PROJECT_DIR=/opt/teraka`

### `POSTGREST_BIN`
- **Description**: Path to postgrest executable
- **Default**: Auto-detected or `./api/postgrest`
- **Use Case**: Non-standard installation location
- **Example**: `POSTGREST_BIN=/usr/local/bin/postgrest`

### `POSTGREST_CONF_PATH`
- **Description**: Path to PostgREST config file
- **Default**: `./api/postgrest.conf`
- **Example**: `POSTGREST_CONF_PATH=/etc/postgrest/postgrest.conf`

---

## Logging Configuration

### `LOG_LEVEL`
- **Description**: Log verbosity
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default**: `INFO`
- **Development**: Use `DEBUG` for verbose output
- **Production**: Use `WARNING` or `ERROR` to reduce noise
- **Example**: `LOG_LEVEL=INFO`

### `LOG_FILE`
- **Description**: Path to Django log file
- **Default**: `/app/logs/django.log` (in Docker)
- **Example**: `LOG_FILE=/var/log/teraka/django.log`

---

## Email Configuration (Optional)

### `EMAIL_BACKEND`
- **Description**: Email backend
- **Options**: `django.core.mail.backends.smtp.EmailBackend`, `django.core.mail.backends.console.EmailBackend`
- **Default**: Console (no real email)

### `EMAIL_HOST`
- **Description**: SMTP server hostname
- **Example**: `EMAIL_HOST=smtp.gmail.com`

### `EMAIL_PORT`
- **Description**: SMTP port
- **Default**: `587` (TLS) or `465` (SSL)
- **Example**: `EMAIL_PORT=587`

### `EMAIL_HOST_USER`
- **Description**: SMTP username
- **Example**: `EMAIL_HOST_USER=noreply@teraka.example.com`

### `EMAIL_HOST_PASSWORD`
- **Description**: SMTP password
- **Security**: Never commit!
- **Example**: `EMAIL_HOST_PASSWORD=your-app-password`

---

## Security Configuration (Production)

### `SECURE_SSL_REDIRECT`
- **Description**: Redirect HTTP to HTTPS
- **Values**: `True`, `False`
- **Default**: `False`
- **Production**: Set to `True`
- **Example**: `SECURE_SSL_REDIRECT=True`

### `SESSION_COOKIE_SECURE`
- **Description**: Only send session cookies over HTTPS
- **Values**: `True`, `False`
- **Default**: `False`
- **Production**: Set to `True`

### `CSRF_COOKIE_SECURE`
- **Description**: Only send CSRF cookies over HTTPS
- **Values**: `True`, `False`
- **Default**: `False`
- **Production**: Set to `True`

### `SECURE_HSTS_SECONDS`
- **Description**: HTTP Strict Transport Security (HSTS) max-age
- **Values**: `0` (disabled) or seconds (e.g., `31536000` = 1 year)
- **Default**: `0`
- **Production**: Set to `31536000` or similar

---

## Docker Compose Specific

### `COMPOSE_PROJECT_NAME`
- **Description**: Project name prefix for containers
- **Default**: `teraka`
- **Result**: Containers named `teraka_postgres`, `teraka_postgrest`, etc.
- **Example**: `COMPOSE_PROJECT_NAME=teraka_prod`

### `COMPOSE_HTTP_TIMEOUT`
- **Description**: Timeout for Docker Compose commands
- **Default**: `60` seconds
- **Example**: `COMPOSE_HTTP_TIMEOUT=120`

### `DEVELOPMENT_MODE`
- **Description**: Enable development features (hot reload, verbose logging)
- **Values**: `0` (production), `1` (development)
- **Default**: `0`
- **Example**: `DEVELOPMENT_MODE=1`

---

## Plugin Configuration (Teraka QGIS Plugin)

### `TERAKA_API_URL` (Plugin)
- **Description**: Django API URL (overrides plugin config)
- **Default**: `http://localhost:8000`
- **Example**: `TERAKA_API_URL=https://api.teraka.example.com`

### `TERAKA_POSTGREST_URL` (Plugin)
- **Description**: PostgREST API URL (overrides plugin config)
- **Default**: `http://localhost:3000`
- **Example**: `TERAKA_POSTGREST_URL=https://api.teraka.example.com:3001`

### `TERAKA_CONFIG_DIR` (Plugin)
- **Description**: Override config directory location
- **Default**: Platform-specific (Windows: `%LOCALAPPDATA%\Teraka`, Linux: `~/.config/Teraka`)
- **Example**: `TERAKA_CONFIG_DIR=/etc/teraka/config`

---

## Common Scenarios

### Development (Local Machine)
```bash
ENV=development
DEBUG=True
DB_USER=postgres
DB_PASSWORD=admin
DJANGO_SECRET_KEY=insecure-dev-key-only
ALLOWED_HOSTS=localhost,127.0.0.1
LOG_LEVEL=DEBUG
```

### Staging (Testing Environment)
```bash
ENV=production
DEBUG=False
DB_USER=teraka_stage
DB_PASSWORD=secure_stage_password_123
DJANGO_SECRET_KEY=generate-new-secret-key
ALLOWED_HOSTS=staging.teraka.example.com
SECURE_SSL_REDIRECT=False
LOG_LEVEL=INFO
```

### Production (Live)
```bash
ENV=production
DEBUG=False
DB_USER=teraka_prod
DB_PASSWORD=very_secure_password_with_special_chars_123!
DJANGO_SECRET_KEY=generate-new-secret-key-never-commit
ALLOWED_HOSTS=teraka.example.com,api.teraka.example.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
LOG_LEVEL=WARNING
```

---

## Setting Environment Variables

### Option 1: `.env` File (Recommended)
```bash
# .env file in project root
DB_PASSWORD=secure_password
DJANGO_SECRET_KEY=your-secret
# Then run:
docker compose --env-file .env up
```

### Option 2: Export in Shell
```bash
export DB_PASSWORD=secure_password
export DJANGO_SECRET_KEY=your-secret
docker compose up
```

### Option 3: Command Line
```bash
docker compose -e DB_PASSWORD=secure -e DJANGO_SECRET_KEY=secret up
```

### Option 4: Docker Secret (Advanced)
For production with sensitive data, use Docker secrets or external secret management (Vault, AWS Secrets Manager, etc.)

---

## Troubleshooting

### Connection refused to PostgREST
- Check `POSTGREST_URL` matches service name in Docker (`postgrest:3000`)
- Check port mappings (`POSTGREST_PORT`)

### Database connection failed
- Check `DB_PASSWORD`, `DB_USER`, `DB_HOST`, `DB_PORT`
- Verify PostgreSQL is running: `docker exec teraka_postgres psql -U postgres -c "SELECT 1"`

### Django returns 500 errors
- Check `LOG_LEVEL=DEBUG` and review logs: `docker logs teraka_backend`
- Check `DJANGO_SECRET_KEY` is set and consistent
- Check `ALLOWED_HOSTS` includes your domain

### CORS errors in plugin
- Check `CORS_ALLOWED_ORIGINS` includes plugin's origin
- Check PostgREST is accessible: `curl http://localhost:3000/`

---

## References

- [Django Settings Reference](https://docs.djangoproject.com/en/stable/ref/settings/)
- [PostgREST Configuration](https://postgrest.org/en/latest/configuration.html)
- [PostgreSQL Environment Variables](https://www.postgresql.org/docs/current/libpq-envars.html)
- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
