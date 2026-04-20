#!/bin/bash
# Script de lancement Teraka pour Linux/macOS
# Utilise le script Python pour lancer les serveurs

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Lancer le script Python
python run_servers.py "$@"
