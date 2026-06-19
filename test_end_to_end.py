#!/usr/bin/env python
"""
Script de test end-to-end pour le système RBAC
Teste:
1. Login des utilisateurs
2. Génération des JWT avec les bons rôles
3. Accès API PostgREST avec enforcement des permissions
"""
import requests
import json
import jwt
from datetime import datetime

# Configuration
DJANGO_URL = 'http://localhost:8000'
TOKEN_ENDPOINT = f'{DJANGO_URL}/api/login/'
POSTGREST_URL = 'http://localhost:3000'

# Utilisateurs de test
TEST_USERS = [
    {'email': 'expansion_l1@teraka.org', 'password': 'test123', 'expected_role': 'Expansion_L1'},
    {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'expected_role': 'Expansion_L2'},
    {'email': 'mrv_l1@teraka.org', 'password': 'test123', 'expected_role': 'MRV_L1'},
    {'email': 'admin_l1@teraka.org', 'password': 'test123', 'expected_role': 'Admin_L1'},
]

# Couleurs ANSI
class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(title):
    print(f"\n{C.BLUE}{C.BOLD}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{C.END}\n")


def print_success(msg):
    print(f"{C.GREEN}✓ {msg}{C.END}")


def print_error(msg):
    print(f"{C.RED}✗ {msg}{C.END}")


def print_info(msg):
    print(f"{C.CYAN}ℹ {msg}{C.END}")


def print_warning(msg):
    print(f"{C.YELLOW}⚠ {msg}{C.END}")


def test_jwt_generation():
    """Test 1: Générer JWT tokens et vérifier les rôles"""
    print_header("TEST 1: Génération de JWT avec les rôles corrects")
    
    # Cas de test additionnel pour la sélection de rôle
    EXTENDED_TESTS = [
        # Défaut (Moindre privilège) -> L1
        {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'requested_role': None, 'expected_role': 'Expansion_L1'},
        # Sélection autorisée (L1)
        {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'requested_role': 'Expansion_L1', 'expected_role': 'Expansion_L1'},
        # Sélection autorisée (L2)
        {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'requested_role': 'Expansion_L2', 'expected_role': 'Expansion_L2'},
        # Sélection interdite (L3 alors que assigné L2) -> Fallback L1
        {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'requested_role': 'EXPANSION', 'expected_role': 'Expansion_L1'},
        # Sélection invalide (Catégorie différente) -> Fallback L1
        {'email': 'expansion_l2@teraka.org', 'password': 'test123', 'requested_role': 'Admin_L1', 'expected_role': 'Expansion_L1'},
    ]

    results = []
    
    # Tests standards
    for user in TEST_USERS:
        email = user['email']
        password = user['password']
        expected_role = user['expected_role']
        
        print(f"{C.YELLOW}Utilisateur:{C.END} {email}")
        
        try:
            # Login
            payload = {'email': email, 'password': password}
            # Par défaut les tests existants s'attendent au rôle complet pour Admin L1, etc.
            # Mais avec notre nouvelle logique, sans spécifier de rôle, ils auront L1 par défaut.
            # Mettons à jour l'attente ou passons le rôle pour rester compatible.
            payload['role'] = expected_role

            response = requests.post(
                TOKEN_ENDPOINT,
                json=payload,
                timeout=5
            )
            
            if response.status_code != 200:
                print_error(f"Login failed (Status: {response.status_code})")
                print(f"  Response: {response.text}")
                results.append(False)
                continue
            
            token_data = response.json()
            access_token = token_data.get('access')
            
            if not access_token:
                print_error("No access token in response")
                results.append(False)
                continue
            
            # Décoder le JWT
            try:
                decoded = jwt.decode(access_token, options={"verify_signature": False})
            except Exception as e:
                print_error(f"Failed to decode JWT: {e}")
                results.append(False)
                continue
            
            # Vérifier le rôle
            token_role = decoded.get('role')
            
            if token_role == expected_role:
                print_success(f"Role correct: '{token_role}'")
                results.append(True)
            else:
                print_error(f"Role mismatch: expected '{expected_role}', got '{token_role}'")
                results.append(False)
            
            # Afficher les autres claims
            print(f"  {C.CYAN}Claims:{C.END}")
            print(f"    • user_id: {decoded.get('user_id')}")
            print(f"    • username: {decoded.get('username')}")
            print(f"    • is_validator: {decoded.get('is_validator')}")
            print(f"    • token_type: {decoded.get('token_type')}")
            
        except requests.exceptions.ConnectionError:
            print_error(f"Cannot connect to {TOKEN_ENDPOINT}")
            print_warning("Make sure Django server is running on port 8000")
            results.append(False)
        except Exception as e:
            print_error(f"Exception: {e}")
            results.append(False)
        
        print()
    
    # Tests de sélection de rôle (Moindre privilège)
    print_header("TEST 1.1: Vérification de la sélection de rôle et moindre privilège")

    for test in EXTENDED_TESTS:
        email = test['email']
        password = test['password']
        requested = test['requested_role']
        expected = test['expected_role']

        print(f"{C.YELLOW}Utilisateur:{C.END} {email}")
        print(f"  Rôle demandé: {requested or 'AUCUN (Défaut)'}")

        try:
            payload = {'email': email, 'password': password}
            if requested:
                payload['role'] = requested

            response = requests.post(TOKEN_ENDPOINT, json=payload, timeout=5)
            access_token = response.json().get('access')
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            token_role = decoded.get('role')

            if token_role == expected:
                print_success(f"Role obtenu: '{token_role}' (Attendu: '{expected}')")
                results.append(True)
            else:
                print_error(f"Role mismatch: expected '{expected}', got '{token_role}'")
                results.append(False)
        except Exception as e:
            print_error(f"Exception: {e}")
            results.append(False)
        print()

    # Résumé
    passed = sum(results)
    total = len(results)
    print(f"{C.BOLD}Résumé Test 1:{C.END} {C.GREEN}{passed}/{total} réussi{C.END}")
    
    return passed == total


def test_postgrest_access():
    """Test 2: Accès API PostgREST avec les rôles"""
    print_header("TEST 2: Accès API PostgREST avec enforcement des permissions")
    
    # Tables de test
    test_cases = [
        {'table': 'communes', 'method': 'GET', 'description': 'Lecture communes'},
        {'table': 'bosquet_suivi', 'method': 'GET', 'description': 'Lecture bosquet_suivi'},
    ]
    
    print_info("Note: PostgREST doit être accessible sur http://localhost:3000")
    
    for user in TEST_USERS[:2]:  # Tester les 2 premiers utilisateurs
        email = user['email']
        password = user['password']
        role = user['expected_role']
        
        print(f"{C.YELLOW}Utilisateur:{C.END} {email} (Rôle: {role})")
        
        try:
            # Obtenir le token
            response = requests.post(
                TOKEN_ENDPOINT,
                json={'email': email, 'password': password},
                timeout=5
            )
            
            if response.status_code != 200:
                print_error("Cannot obtain token")
                continue
            
            access_token = response.json().get('access')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Tester chaque table
            for test_case in test_cases:
                table = test_case['table']
                method = test_case['method']
                desc = test_case['description']
                
                url = f'{POSTGREST_URL}/{table}?limit=1'
                
                try:
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=5)
                    else:
                        response = requests.post(url, headers=headers, timeout=5)
                    
                    status = response.status_code
                    
                    if status in [200, 201]:
                        print_success(f"{desc}: {status}")
                    elif status == 403:
                        print_warning(f"{desc}: {status} (Forbidden - Expected)")
                    else:
                        print_error(f"{desc}: {status}")
                        
                except requests.exceptions.ConnectionError:
                    print_warning(f"PostgREST not accessible")
                    break
                except Exception as e:
                    print_error(f"{desc}: {str(e)[:50]}")
            
        except Exception as e:
            print_error(f"Error: {e}")
        
        print()


def test_admin_interface():
    """Test 3: Vérifier l'interface admin"""
    print_header("TEST 3: Interface Admin Django")
    
    print_info("L'interface admin est accessible à:")
    print(f"  {C.CYAN}{DJANGO_URL}/admin/core/userrole/{C.END}")
    print()
    print_info("Instructions:")
    print("  1. Allez à l'URL ci-dessus")
    print("  2. Connectez-vous avec un compte superuser (ex: django/admin)")
    print("  3. Vous devriez voir tous les utilisateurs avec leurs rôles assignés")
    print("  4. Vous pouvez cliquer sur un utilisateur pour modifier son rôle")
    print()


def main():
    """Exécuter tous les tests"""
    print(f"\n{C.BOLD}{C.BLUE}{'*'*70}")
    print("TEST END-TO-END: Système RBAC avec JWT et PostgREST")
    print(f"{'*'*70}{C.END}\n")
    
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Django: {DJANGO_URL}")
    print_info(f"PostgREST: {POSTGREST_URL}")
    print()
    
    try:
        # Test 1: JWT Generation
        test1_passed = test_jwt_generation()
        
        # Test 2: PostgREST Access
        test_postgrest_access()
        
        # Test 3: Admin Interface
        test_admin_interface()
        
        # Summary
        print_header("RÉSUMÉ COMPLET")
        
        if test1_passed:
            print_success("JWT tokens générés avec les rôles corrects")
            print_success("Système RBAC est opérationnel")
            print()
            print(f"{C.BOLD}Prochaines étapes:{C.END}")
            print("  1. Vérifier PostgREST est bien lancé et reçoit les tokens")
            print("  2. Tester les permissions en détail par rôle")
            print("  3. Valider les restrictions d'accès pour chaque table")
            print("  4. Mettre en place la documentation pour les utilisateurs")
        else:
            print_error("Certains tests ont échoué")
            print_warning("Vérifiez:")
            print("  1. Le serveur Django est en cours d'exécution")
            print("  2. Les mots de passe des utilisateurs sont corrects")
            print("  3. La base de données est accessible")
        
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Tests interrompus par l'utilisateur{C.END}")
    except Exception as e:
        print_error(f"Erreur globale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
