#!/bin/bash
# Quick deployment script for Teraka backend
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

ENV=${1:-staging}
echo "🚀 Deploying Teraka backend to: $ENV"

# Step 1: Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Step 2: Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 3: Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Step 4: Sync Django Groups with PostgreSQL Roles
echo "🔄 Syncing Django Groups with PostgreSQL Roles..."
python manage.py sync_groups_roles --create

# Step 5: Collect static files (if needed)
echo "📄 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Step 6: Restart services
if [ "$ENV" = "production" ]; then
    echo "🔄 Restarting Gunicorn..."
    systemctl restart gunicorn
elif [ "$ENV" = "staging" ]; then
    echo "🔄 Restarting Gunicorn (staging)..."
    systemctl restart gunicorn-staging || true
fi

echo "✅ Deployment complete!"
echo ""
echo "Verify:"
echo "  - Django Admin: http://localhost:8000/admin/"
echo "  - RBAC Hub: http://localhost:8000/admin/rbac/"
echo "  - Check Groups: python manage.py sync_groups_roles"
