@echo off
setlocal

@echo off
REM Script de lancement Teraka pour Windows
REM Utilise le script Python pour lancer les serveurs

setlocal enabledelayedexpansion

REM Récupérer le répertoire du script
set SCRIPT_DIR=%~dp0

REM Changer vers le répertoire du projet
cd /d "%SCRIPT_DIR%"

::Activer le coeur de Miniconda en arrière-plan (indispensable pour les DLL comme GDAL)
call "C:\Users\johro\miniconda3\Scripts\activate.bat" "C:\Users\johro\miniconda3"


::Executer le script Python dans ce contexte securise
python run_servers.py

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Le script run_servers.py a rencontre un probleme !
) else (
    echo.
    echo [SUCCES] Le script s'est execute.
)

pause
