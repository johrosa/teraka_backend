   fix_migration.bat@echo off
REM Script Windows pour corriger le problème de migration
REM Exécutez en tant qu'administrateur dans le dossier backend_django

echo.
echo =========================================================
echo FIX: Erreur "relation core_userrole already exists"
echo =========================================================
echo.
echo Etape 1: Suppression de l'enregistrement de migration...
echo.

REM Utiliser psql pour nettoyer
psql -U postgres -d teraka -c "DELETE FROM django_migrations WHERE app = 'core' AND name = '0002_userrole_auditlog';"

if %ERRORLEVEL% EQU 0 (
    echo ✓ Nettoyage reussi
    echo.
    echo Etape 2: Application de la migration...
    echo.
    python manage.py migrate core
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo =========================================================
        echo ✓ SUCCES! Les migrations sont maintenant appliquees.
        echo =========================================================
        echo.
        echo Prochaines etapes:
        echo - Relancer le serveur Django
        echo - Visiter http://localhost:8000/admin/dashboard/
        echo.
    ) else (
        echo ✗ Erreur lors de la migration
        pause
        exit /b 1
    )
) else (
    echo ✗ Erreur lors du nettoyage des migrations
    echo.
    echo Assurez-vous que:
    echo - PostgreSQL est en cours d'execution
    echo - La base de donnees 'teraka' existe
    echo - L'utilisateur 'postgres' a les bons droits
    echo.
    pause
    exit /b 1
)

pause

