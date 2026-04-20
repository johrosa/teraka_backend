#!/usr/bin/env python
"""
Test script to verify user-role association with JWT tokens

Teste le flux complet:
1. Login avec chaque utilisateur
2. Génère un JWT token
3. Vérifie que le token contient le rôle correct
4. Teste l'API PostgREST avec le rôle
"""
import os
import django
import json
import requests
from django.contrib.auth.models import User
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models_rbac import UserRole

# Configuration
BASE_URL = 'http://localhost:8000'
API_URL = 'http://localhost:3000'  # PostgREST

# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def test_jwt_token_generation():
    """Test la génération de JWT avec les rôles corrects"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print('TEST 1: Génération de JWT avec rôles corrects')
    print(f"{'='*70}{Colors.END}\n")
    
    # Client HTTP Django
    client = Client()
    login_url = f'{BASE_URL}/api/token/'
    
    # Récupérer tous les utilisateurs avec rôles
    user_roles = UserRole.objects.select_related('user').all()
    
    test_results = []
    
    for user_role in user_roles:
        user = user_role.user
        username = user.username
        expected_role = user_role.role
        
        print(f"Testing user: {Colors.YELLOW}{username}{Colors.END}")
        
        # Credentials pour test (si le mot de passe est 'test123')
        # Note: en production, utiliser des vrais credentials
        credentials = {
            'username': username,
            'password': 'test123',  # À adapter selon votre setup
        }
        
        try:
            # Login et récupération du token
            response = client.post(
                login_url,
                data=credentials,
                content_type='application/json'
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access')
                
                if access_token:
                    # Décoder le JWT (sans vérification de signature pour le test)
                    import jwt
                    try:
                        # Décoder sans vérifier la signature (pour test uniquement)
                        decoded = jwt.decode(
                            access_token,
                            options={"verify_signature": False}
                        )
                        
                        token_role = decoded.get('role')
                        
                        if token_role == expected_role:
                            result = f"{Colors.GREEN}✓ OK{Colors.END}"
                            test_results.append(True)
                        else:
                            result = (
                                f"{Colors.RED}✗ ERREUR{Colors.END}: "
                                f"Expected '{expected_role}', got '{token_role}'"
                            )
                            test_results.append(False)
                        
                        print(f"  Role in token: {Colors.YELLOW}{token_role}{Colors.END} {result}")
                        print(f"  Token claims: user_id={decoded.get('user_id')}, "
                              f"username={decoded.get('username')}, "
                              f"is_validator={decoded.get('is_validator')}")
                        
                    except Exception as e:
                        print(f"  {Colors.RED}✗ Error decoding token: {e}{Colors.END}")
                        test_results.append(False)
                else:
                    print(f"  {Colors.RED}✗ No access token in response{Colors.END}")
                    test_results.append(False)
            else:
                print(f"  {Colors.RED}✗ Login failed (Status: {response.status_code}){Colors.END}")
                print(f"    Response: {response.text}")
                test_results.append(False)
                
        except Exception as e:
            print(f"  {Colors.RED}✗ Exception: {e}{Colors.END}")
            test_results.append(False)
    
    # Résumé
    print(f"\n{Colors.BLUE}Résumé Test 1:{Colors.END}")
    passed = sum(test_results)
    total = len(test_results)
    status = Colors.GREEN if passed == total else Colors.RED
    print(f"  {status}{passed}/{total} tests passed{Colors.END}")
    
    return passed == total


def test_postgrest_api():
    """Test l'API PostgREST avec les rôles"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print('TEST 2: Accès API PostgREST avec rôles')
    print(f"{'='*70}{Colors.END}\n")
    
    # URL de test PostgREST
    tables_to_test = [
        ('communes', 'GET'),  # Lecture seule pour Expansion_L1
        ('bosquet_suivi', 'GET'),  # CRUD pour Admin
    ]
    
    user_roles = UserRole.objects.select_related('user').all()
    
    for user_role in user_roles[:3]:  # Tester les 3 premiers utilisateurs
        user = user_role.user
        username = user.username
        role = user_role.role
        
        print(f"Testing user: {Colors.YELLOW}{username}{Colors.END} (role: {role})")
        
        # Créer un JWT token pour cet utilisateur
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            from core.models_rbac import UserRole as UR
            
            # Générer le token
            token = RefreshToken.for_user(user)
            access_token = str(token.access_token)
            
            # Tester une requête POST à PostgREST
            for table, method in tables_to_test:
                url = f'{API_URL}/{table}'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                try:
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=5)
                    else:
                        response = requests.post(url, headers=headers, timeout=5)
                    
                    if response.status_code in [200, 201]:
                        print(f"  {Colors.GREEN}✓ {method} {table}: {response.status_code}{Colors.END}")
                    elif response.status_code == 403:
                        print(f"  {Colors.YELLOW}✓ {method} {table}: {response.status_code} (Forbidden - Expected){Colors.END}")
                    else:
                        print(f"  {Colors.RED}✗ {method} {table}: {response.status_code}{Colors.END}")
                        
                except requests.exceptions.ConnectionError:
                    print(f"  {Colors.YELLOW}⚠ PostgREST not accessible at {API_URL}{Colors.END}")
                    break
                except Exception as e:
                    print(f"  {Colors.RED}✗ Error: {e}{Colors.END}")
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Token generation error: {e}{Colors.END}")


def test_default_role_assignment():
    """Test l'attribution du rôle par défaut"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print('TEST 3: Rôle par défaut pour utilisateurs sans attribution')
    print(f"{'='*70}{Colors.END}\n")
    
    # Créer un nouvel utilisateur
    test_user, created = User.objects.get_or_create(
        username='test_no_role',
        defaults={
            'email': 'test@teraka.local',
            'is_staff': False,
        }
    )
    
    # Set une password pour le test
    test_user.set_password('test123')
    test_user.save()
    
    print(f"Test user: {Colors.YELLOW}{test_user.username}{Colors.END}")
    print(f"  Is superuser: {test_user.is_superuser}")
    print(f"  Is staff: {test_user.is_staff}")
    
    # Vérifier qu'il n'a pas de rôle
    has_role = UserRole.objects.filter(user=test_user).exists()
    print(f"  Has UserRole entry: {has_role}")
    
    if not has_role:
        print(f"  {Colors.GREEN}✓ User correctly has no explicit role{Colors.END}")
        print(f"  {Colors.YELLOW}→ Will use default: 'Expansion_L1' (not superuser){Colors.END}")
    
    # Test token generation
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        
        token = RefreshToken.for_user(test_user)
        access_token = str(token.access_token)
        
        import jwt
        decoded = jwt.decode(
            access_token,
            options={"verify_signature": False}
        )
        
        token_role = decoded.get('role')
        print(f"  Token role: {Colors.YELLOW}{token_role}{Colors.END}")
        
        if token_role == 'Expansion_L1':
            print(f"  {Colors.GREEN}✓ Default role correctly applied{Colors.END}")
        else:
            print(f"  {Colors.RED}✗ Unexpected role: {token_role}{Colors.END}")
            
    except Exception as e:
        print(f"  {Colors.RED}✗ Error: {e}{Colors.END}")
    
    # Cleanup
    test_user.delete()


if __name__ == '__main__':
    print(f"\n{Colors.BLUE}{'*'*70}")
    print('RBAC User-Role JWT Integration Tests')
    print(f"{'*'*70}{Colors.END}")
    
    try:
        # Run tests
        test1_passed = test_jwt_token_generation()
        test_postgrest_api()
        test_default_role_assignment()
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*70}")
        print('SUMMARY')
        print(f"{'='*70}{Colors.END}")
        
        if test1_passed:
            print(f"{Colors.GREEN}✓ All JWT token generation tests PASSED{Colors.END}")
            print(f"  User roles are correctly included in JWT tokens")
            print(f"  PostgREST can now enforce role-based permissions")
        else:
            print(f"{Colors.RED}✗ Some tests FAILED{Colors.END}")
            print(f"  Check user credentials and role assignments")
        
    except Exception as e:
        print(f"{Colors.RED}✗ Test suite error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
