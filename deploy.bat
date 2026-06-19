@echo off
REM Quick deployment script for Teraka backend (Windows)
REM Usage: deploy.bat [environment]
REM Example: deploy.bat production

setlocal enabledelayedexpansion

set ENV=%1
if "%ENV%"=="" set ENV=staging

echo.
echo ========================================
echo 🚀 Deploying Teraka backend to: %ENV%
echo ========================================
echo.

REM Step 1: Pull latest code
echo 📥 Pulling latest code...
git pull origin main
if errorlevel 1 (
    echo [ERROR] Git pull failed
    exit /b 1
)

REM Step 2: Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Pip install failed
    exit /b 1
)

REM Step 3: Run migrations
echo 🗄️  Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migrations failed
    exit /b 1
)

REM Step 4: Sync Django Groups with PostgreSQL Roles
echo 🔄 Syncing Django Groups with PostgreSQL Roles...
python manage.py sync_groups_roles --create
if errorlevel 1 (
    echo [WARNING] Sync command had issues (may be expected)
)

REM Step 5: Collect static files (if needed)
echo 📄 Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [WARNING] Static files collection had issues (may be optional)
)

REM Step 6: Display completion info
echo.
echo ========================================
echo ✅ Deployment complete!
echo ========================================
echo.
echo Verify:
echo   - Django Admin: http://localhost:8000/admin/
echo   - RBAC Hub: http://localhost:8000/admin/rbac/
echo   - Check Groups: python manage.py sync_groups_roles
echo.
echo Next steps:
echo   1. Restart your Django/Gunicorn server manually
echo   2. Check logs for any errors
echo   3. Test admin interface
echo.

endlocal
