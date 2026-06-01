#!/bin/bash
# Initialize Teraka backend project
# Creates necessary directories and templates

set -e

echo "🔧 Initializing Teraka Backend Project..."

# Create necessary directories
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p config

echo "✓ Created directories: logs, media, staticfiles, config"

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from template"
    echo "  ⚠️  WARNING: Edit .env with your configuration before deploying!"
else
    echo "✓ .env already exists (skipped copy)"
fi

# Create plugin_config.json.example if needed
PLUGIN_CONFIG_TEMPLATE="{
  \"api\": {
    \"django_url\": \"http://localhost:8000\",
    \"postgrest_url\": \"http://localhost:3000\",
    \"timeout_seconds\": 30
  },
  \"features\": {
    \"enable_offline_mode\": false,
    \"auto_sync_interval_minutes\": 60
  }
}"

if [ ! -f config/plugin_config.json ]; then
    echo "$PLUGIN_CONFIG_TEMPLATE" > config/plugin_config.json
    echo "✓ Created config/plugin_config.json template"
fi

echo ""
echo "✅ Project initialized successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env with your environment-specific settings"
echo "   2. Edit config/plugin_config.json if needed"
echo "   3. Run: docker compose -f docker-compose.prod.yml up --build"
echo ""
echo "📖 For more information:"
echo "   - Documentation: see README.md"
echo "   - Environment variables: see ENVIRONMENT_VARIABLES.md"
echo "   - Backend paths: see BACKEND_PATH_ISSUES.md"
echo ""
