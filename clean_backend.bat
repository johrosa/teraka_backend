@echo off
SETLOCAL EnableDelayedExpansion

echo =========================================================
echo Teraka Backend: Environment Check and Database Cleanup
echo =========================================================

:: 1. Check Environment Files
if not exist .env (
    echo [WARNING] .env file not found.
    if exist .env.example (
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env
        echo [IMPORTANT] Please edit .env with your DB credentials before continuing.
        pause
    ) else (
        echo [ERROR] No .env or .env.example found. Database commands will fail.
        pause
        exit /b 1
    )
)

:: 2. Check Python & GDAL installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b 1
)

:: Check for GDAL (required by Django GIS and your import script)
echo %PATH% | findstr /I "gdal" >nul
if %errorlevel% neq 0 (
    echo [WARNING] GDAL not found in PATH. 
    echo If "pip install GDAL" fails, ensure OSGeo4W is installed and configured.
)

:: 3. Verify requirements
echo [INFO] Verifying and installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

:: 4. Run Migrations
echo [INFO] Ensuring database schema is up to date...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration failed. Check your DB_HOST and credentials in .env.
    pause
    exit /b 1
)

:: 5. Clean Database
echo [INFO] cleaning database...
echo WARNING: This will delete data in Django-managed tables AND custom SQL tables.
set /p confirm="Are you sure you want to proceed with a full cleanup? (y/n): "

if /i "%confirm%"=="y" (
    echo [INFO] Flushing Django-managed tables...
    python manage.py flush --no-input
    
    :: Handling custom tables/logs (since you mentioned they exist via raw SQL)
    :: If you have a custom cleanup script, uncomment the following line:
    :: psql -U %DB_USER% -d %DB_NAME% -f custom_cleanup.sql

    :: Optional: Running your specific QGIS import clean-up
    :: python manage.py import_qgis_data "path/to/project.qgs" --clear
    
    echo [SUCCESS] Database cleanup completed.
) else (
    echo [INFO] Cleanup cancelled by user.
)

echo [DONE]
pause
