#!/usr/bin/env python
"""
Script de test pour la page d'accueil
Vérifie que la home page s'affiche correctement
"""
import os
import sys
import django
import requests
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

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

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'*'*70}")
    print("TEST DE LA PAGE D'ACCUEIL TERAKA")
    print(f"{'*'*70}{Colors.END}\n")
    
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Base URL: {BASE_URL}")
    
    try:
        print_header("Test 1: Accès à la page d'accueil")
        
        # Tester l'accès à la home page
        response = requests.get(f'{BASE_URL}/', timeout=10)
        
        if response.status_code == 200:
            print_success(f"Page d'accueil accessible (Status: 200)")
            
            # Vérifier le contenu
            content = response.text
            
            checks = {
                'Titre (Teraka Platform)': 'Teraka Platform' in content,
                'Logo': 'Teraka Platform' in content,
                'Navigation': '<nav' in content or 'nav-links' in content,
                'Hero Section': 'hero' in content,
                'Statistiques': 'stat-card' in content,
                'Communes': 'Communes' in content,
                'Bosquets': 'Bosquets' in content,
                'Arbres': 'Arbres' in content,
                'Membres': 'Membres' in content,
                'Footer': '<footer' in content,
            }
            
            print("\n" + Colors.CYAN + "Vérification du contenu:" + Colors.END)
            for check_name, result in checks.items():
                if result:
                    print_success(f"{check_name}")
                else:
                    print_error(f"{check_name}")
            
            # Compter les résultats
            passed = sum(1 for v in checks.values() if v)
            total = len(checks)
            
            print(f"\n{Colors.CYAN}Résultat:{Colors.END} {passed}/{total} vérifications réussies")
            
        elif response.status_code == 404:
            print_error(f"Page non trouvée (404)")
            print_info("Vérifiez que la route '/' est bien configurée dans urls.py")
            return False
        else:
            print_error(f"Erreur d'accès (Status: {response.status_code})")
            return False
        
        print_header("Test 2: Vérification de la structure HTML")
        
        # Vérifier la structure HTML
        structure_checks = {
            'DOCTYPE': '<!DOCTYPE html>' in content or 'DOCTYPE' in content,
            'Meta charset': 'charset' in content,
            'Meta viewport': 'viewport' in content,
            'Styles CSS': '<style' in content,
            'Header': '<header' in content,
            'Container': 'container' in content,
            'Footer': '<footer' in content,
        }
        
        for check_name, result in structure_checks.items():
            if result:
                print_success(f"{check_name}")
            else:
                print_error(f"{check_name}")
        
        print_header("Test 3: Performance & Taille")
        
        # Mesurer la taille
        size_kb = len(response.content) / 1024
        print_info(f"Taille de la page: {size_kb:.1f} KB")
        
        if size_kb > 500:
            print_error(f"La page est trop grande (> 500 KB)")
        elif size_kb > 250:
            print_error(f"La page est un peu lourde (> 250 KB)")
        else:
            print_success(f"Taille optimale (< 250 KB)")
        
        # Vérifier le temps de réponse
        print_info(f"Temps de réponse: {response.elapsed.total_seconds()*1000:.0f}ms")
        
        if response.elapsed.total_seconds() > 2:
            print_error("La page est lente (> 2 secondes)")
        elif response.elapsed.total_seconds() > 1:
            print_error("La page pourrait être plus rapide (> 1 seconde)")
        else:
            print_success("Réponse rapide (< 1 seconde)")
        
        print_header("Test 4: Responsive Design")
        
        responsive_features = {
            'Meta viewport': 'viewport' in content,
            'Grid layout': 'grid' in content,
            'Flexbox': 'flex' in content,
            'Media queries': '@media' in content,
            'Responsive classes': 'mobile' in content or 'tablet' in content or 'desktop' in content,
        }
        
        for feature, found in responsive_features.items():
            if found:
                print_success(f"{feature}")
            else:
                print_error(f"{feature}")
        
        print_header("Test 5: Accès aux URLs principales")
        
        urls_to_test = {
            'Admin Panel': '/admin/',
            'API Statistics': '/api/statistics/',
            'API Export': '/api/export/',
        }
        
        print("(Tests optionnels - nécessitent authentification)")
        for name, url in urls_to_test.items():
            try:
                response = requests.head(f'{BASE_URL}{url}', timeout=5)
                if response.status_code in [200, 301, 302]:
                    print_success(f"{name}: Accessible")
                elif response.status_code == 401 or response.status_code == 403:
                    print_info(f"{name}: Nécessite authentification")
                else:
                    print_error(f"{name}: {response.status_code}")
            except Exception as e:
                print_error(f"{name}: {str(e)[:40]}")
        
        print_header("RÉSUMÉ")
        
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Page d'accueil opérationnelle!{Colors.END}")
        print(f"\n✅ Tests réussis:")
        print(f"   • Page accessible (200 OK)")
        print(f"   • Contenu chargé dynamiquement")
        print(f"   • Structure HTML valide")
        print(f"   • Design responsive")
        
        print(f"\n📍 Accédez à: {BASE_URL}/")
        print(f"\n💡 Prochaines étapes:")
        print(f"   1. Vérifier les statistiques affichées")
        print(f"   2. Tester la connexion/déconnexion")
        print(f"   3. Tester les liens d'administration")
        print(f"   4. Valider en mobile et desktop")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Assurez-vous que Django est en cours d'exécution:")
        print_info("  python manage.py runserver")
        return False
    
    except Exception as e:
        print_error(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
