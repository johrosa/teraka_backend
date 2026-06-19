# Teraka Backend

This repository contains the backend services for the Teraka platform, including the Django web application, PostgreSQL/PostGIS database support, and PostgREST API exposure.

## Purpose

The backend provides:
- Django-based REST and admin services
- PostgREST API access to database tables and views
- PostGIS-enabled spatial data storage
- Authentication and authorization for the Teraka frontend and plugin clients

## Architecture

The production-like stack includes:
- `postgres` (PostGIS) for spatial database storage
- `postgrest` for automatically exposing database tables as REST endpoints
- `backend` running Django application via Gunicorn (or Django `runserver` on Windows)
- `adminer` for optional database web administration

## Key files

- `Dockerfile` — builds the backend image with Python, GDAL, and project dependencies
- `docker-compose.prod.yml` — production-like Docker Compose configuration
- `api/postgrest.conf` — PostgREST server configuration mounted into the container
- `run_servers.py` — unified launcher for Django and PostgREST in local / development mode
- `requirements.txt` — Python dependencies

## Documentation

- [Environment variables](ENVIRONMENT_VARIABLES.md) — configuration values for Django, PostgreSQL, PostgREST, CORS, and local tooling.
- [RBAC guide](RBAC_GUIDE.md) — current admin workflow for role-based access control.
- [Groups/Roles deployment](DEPLOYMENT_GROUPS_ROLES_SYNC.md) — sync Django Groups with PostgreSQL Roles on deployment.
- [Management API reference](API_MANAGEMENT_VIEWS.md) — backend monitoring, validation, statistics, and export endpoints.
- [Troubleshooting](TROUBLESHOOTING.md) — common startup and runtime issues.

## Deployment

### Docker Compose (recommended)

From `backend_django/`:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

This starts:
- `postgres` on port `5432`
- `postgrest` on port `3000`
- `backend` (Django) on port `8000`
- `adminer` on port `8080`

### Standalone backend image

Build only the backend image from `backend_django/`:

```bash
docker build -t teraka_backend .
```

Run the backend container connected to an existing PostgreSQL database:

```bash
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgres://postgres:admin@host:5432/teraka \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  teraka_backend
```

### Docker Compose pre-steps

Before starting the stack, ensure the database has the required Postgres role and schema permissions for PostgREST.

```bash
docker compose -f docker-compose.prod.yml up -d postgres
```

Then create the anonymous role:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres psql -U ${DB_USER:-postgres} -d ${DB_NAME:-teraka} -c "CREATE ROLE web_anon NOLOGIN; GRANT USAGE ON SCHEMA public TO web_anon;"
```

### Environment variables

The Compose file uses the following env vars with defaults:

- `DB_USER` — default `postgres`
- `DB_PASSWORD` — default `admin`
- `DB_NAME` — default `teraka`
- `DB_PORT` — default `5432`
- `DJANGO_PORT` — default `8000`
- `POSTGREST_PORT` — default `3000`
- `ENV` — default `production`
- `DEBUG` — default `False`
- `DJANGO_SECRET_KEY` — default `change-me-in-production`
- `ALLOWED_HOSTS` — default `localhost,127.0.0.1`

For local use, create a `.env` file or export the variables before launching.

### Using the bundled PostgREST config

The `postgrest` service mounts `./api/postgrest.conf` into the container and starts PostgREST with that config file.

Important settings in `api/postgrest.conf`:
- `db-uri` — points to the PostgreSQL service
- `db-schema` — usually `public`
- `db-anon-role` — should match the table access role (`web_anon`)
- `jwt-secret` — must match the Django JWT signing key if JWT authentication is used
- `server-host` — set to `0.0.0.0` for Docker container binding
- `server-port` — set to `3000`

### Running locally without Docker

On Windows, use the launcher script and the local Python environment:

```bash
python run_servers.py --env production
```

Note: on Windows, `run_servers.py` falls back to Django `runserver` for production mode because Gunicorn depends on `fcntl`.

### Database Migrations

After pulling new code or setting up the environment, always run migrations to apply schema changes:

```bash
python manage.py migrate
```

This applies all pending migrations from the core app (and other Django apps) in sequence:
- `0001_initial` — initial schema
- `0002_role_model` — UserRole and Role models
- `0003_fieldmapping` — FieldMapping model for QGIS integration
- `0004_add_users_role_enum_rbac_roles` — PostgreSQL role enum and RBAC configuration
- `0005_audit_log` — tamper-evident audit log table, pgcrypto function, and triggers
- `0006_alter_userrole_options` — UserRole metadata updates
- `0007_audit_view` — readable audit view joining with user emails
- `0008-0014_*` — User auth fields, UUID defaults, FK conversions

**Important for Docker environments:**
If running Docker Compose, execute migrations within the container:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Django Groups ↔ PostgreSQL Roles Sync

After deployment, synchronize Django Groups with PostgreSQL Roles and RBAC permissions:

```bash
# Sync roles/groups
python manage.py sync_groups_roles --create
# Preview permission sync
python manage.py sync_rbac_permissions --dry-run
# Apply permission sync
python manage.py sync_rbac_permissions --create
```

This ensures:
- All PostgreSQL roles have corresponding Django Groups
- All Django Groups have corresponding Roles
- Signals keep them in sync automatically going forward

**For deployment checklist, see:** [DEPLOYMENT_GROUPS_ROLES_SYNC.md](DEPLOYMENT_GROUPS_ROLES_SYNC.md)

## Access URLs

- Django admin: `http://localhost:8000/admin/`
- Login API: `http://localhost:8000/api/login/`
- PostgREST API: `http://localhost:3000`
- Adminer: `http://localhost:8080`

## Notes

- The folder `api/postgrest.conf` is intentionally mounted into the PostgREST container for configuration consistency.
- The production Docker stack uses Gunicorn for Django on Linux/macOS, while Windows uses Django's development server as a compatibility fallback.
- If you change database credentials, update both the compose env vars and `api/postgrest.conf` accordingly.
