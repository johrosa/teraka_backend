#!/usr/bin/env python
"""
Script de test pour les API de gestion de plateforme
Teste tous les endpoints et affiche les résultats
"""
import os
import sys
import django
import requests
from datetime import datetime

from _project_path import ensure_project_root

ensure_project_root()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Configuration
BASE_URL = 'http://localhost:8000'

# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def get_admin_token():
    """Génère un JWT token pour un utilisateur admin"""
    try:
        # Chercher un admin existant
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print_error("Aucun admin trouvé. Créez un superuser d'abord:")
            print(f"  python manage.py createsuperuser")
            return None
        
        # Générer le token
        refresh = RefreshToken.for_user(admin_user)
        token = str(refresh.access_token)
        
        print_success(f"Token généré pour: {admin_user.username}")
        return token
    
    except Exception as e:
        print_error(f"Erreur lors de la génération du token: {e}")
        return None

def test_endpoint(session, token, method, endpoint, data=None):
    """Teste un endpoint et affiche le résultat"""
    url = f'{BASE_URL}{endpoint}'
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        if method == 'GET':
            response = session.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            headers['Content-Type'] = 'application/json'
            response = session.post(url, headers=headers, json=data, timeout=10)
        else:
            print_error(f"Méthode HTTP non supportée: {method}")
            return False
        
        if response.status_code in [200, 201]:
            print_success(f"{method} {endpoint} - {response.status_code}")
            try:
                json_data = response.json()
                # Afficher les informations principales
                if 'timestamp' in json_data:
                    print(f"  Timestamp: {json_data['timestamp']}")
                if 'status' in json_data:
                    print(f"  Status: {json_data['status']}")
                if 'summary' in json_data:
                    summary = json_data['summary']
                    for key, value in summary.items():
                        print(f"  {key}: {value}")
                if 'platform' in json_data:
                    platform = json_data['platform']
                    for key, value in platform.items():
                        print(f"  {key}: {value}")
            except:
                pass
            return True
        elif response.status_code == 401:
            print_error(f"{method} {endpoint} - 401 Unauthorized")
            return False
        elif response.status_code == 403:
            print_error(f"{method} {endpoint} - 403 Forbidden")
            return False
        else:
            print_error(f"{method} {endpoint} - {response.status_code}")
            print(f"  Response: {response.text[:100]}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Assurez-vous que Django est en cours d'exécution:")
        print_info("  python manage.py runserver")
        return False
    
    except Exception as e:
        print_error(f"Erreur lors de {method} {endpoint}: {str(e)[:60]}")
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'*'*70}")
    print("TEST DES API DE GESTION DE PLATEFORME TERAKA")
    print(f"{'*'*70}{Colors.END}\n")
    
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Base URL: {BASE_URL}")
    
    # Obtenir le token
    token = get_admin_token()
    if not token:
        sys.exit(1)
    
    # Créer une session requests
    session = requests.Session()
    
    # Liste des endpoints à tester
    endpoints_to_test = [
        # Statistics
        ('GET', '/api/statistics/', None, 'Statistiques globales'),
        ('GET', '/api/bosquet-statistics/', None, 'Statistiques par bosquet'),
        ('GET', '/api/members-by-region/', None, 'Membres par région'),
        ('GET', '/api/data-quality/', None, 'Rapport de qualité'),
        
        # Validation & Health
        ('GET', '/api/data-validation/', None, 'Validation des données'),
        ('GET', '/api/system-health/', None, 'Santé du système'),
        
        # Activity & Logs
        ('GET', '/api/user-activity/', None, 'Journal d\'activité'),
        
        # Export
        ('POST', '/api/export/', {'format': 'json', 'tables': ['bosquets']}, 'Export de données'),
    ]
    
    # Tester chaque endpoint
    print_header("RÉSULTATS DES TESTS")
    
    results = []
    for method, endpoint, data, description in endpoints_to_test:
        print(f"\n{Colors.YELLOW}🧪 {description}{Colors.END}")
        result = test_endpoint(session, token, method, endpoint, data)
        results.append(result)
    
    # Résumé
    print_header("RÉSUMÉ")
    
    passed = sum(results)
    total = len(results)
    status = Colors.GREEN if passed == total else Colors.RED
    
    print(f"{status}{passed}/{total} endpoints testés avec succès{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Tous les tests sont passés!{Colors.END}")
        print(f"\n📚 Documentation complète disponible:")
        print(f"   API_MANAGEMENT_VIEWS.md")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Certains tests ont échoué{Colors.END}")
        print(f"\nVérifiez:")
        print(f"  1. Django est en cours d'exécution")
        print(f"  2. La base de données est accessible")
        print(f"  3. Les modèles sont correctement migré")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
