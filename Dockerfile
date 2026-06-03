FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Définir les variables GDAL
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copier le code de l'application
COPY . .

# Créer les répertoires pour les logs et media
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Donner les permissions
RUN chmod +x run_servers.py run_servers.sh

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Exposer le port Django
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Lancer l'application Django via Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=120"]
