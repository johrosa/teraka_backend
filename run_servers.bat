@echo off
REM Script de lancement Teraka pour Windows
REM Utilise le script Python pour lancer les serveurs

setlocal enabledelayedexpansion

REM Récupérer le répertoire du script
set SCRIPT_DIR=%~dp0

REM Changer vers le répertoire du projet
cd /d "%SCRIPT_DIR%"

REM Vérifier si conda est disponible et l'environnement est activé
if defined CONDA_DEFAULT_ENV (
    echo Environnement Conda détecté: !CONDA_DEFAULT_ENV!
) else (
    REM Chercher à activer l'environnement conda
    if exist "%CONDA_PREFIX%\Scripts\activate.bat" (
        call "%CONDA_PREFIX%\Scripts\activate.bat" backend_django
    )
)

REM Lancer le script Python
python run_servers.py %*

pause
