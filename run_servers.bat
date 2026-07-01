@echo off
REM Script de lancement Teraka pour Windows
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM 1. Vérifier si un environnement Conda est déjà actif
if defined CONDA_DEFAULT_ENV (
    echo Environnement Conda détecté: !CONDA_DEFAULT_ENV!
    goto :LAUNCH
)

REM 2. Tenter de localiser Conda via les chemins standards de l'utilisateur
set "CONDA_ACTIVATE="
if exist "%CONDA_PREFIX%\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%CONDA_PREFIX%\Scripts\activate.bat"
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%USERPROFILE%\miniconda3\Scripts\activate.bat"
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else if exist "%ProgramData%\miniconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%ProgramData%\miniconda3\Scripts\activate.bat"
) else if exist "%ProgramData%\anaconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%ProgramData%\anaconda3\Scripts\activate.bat"
)

REM 3. Activer l'environnement si le script est trouvé
if defined CONDA_ACTIVATE (
    echo Activation de l'environnement avec !CONDA_ACTIVATE!
    call "!CONDA_ACTIVATE!" teraka
) else (
    echo [ATTENTION] Conda n'a pas ete trouve automatiquement.
    echo Assurez-vous que Python ou Conda est dans votre PATH.
)

:LAUNCH
REM 4. Lancer le script Python
python run_servers.py %*

popd
pause