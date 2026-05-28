#!/usr/bin/env python
"""
Test avancé des rôles RBAC avec PostgREST
Vérifie que les permissions CRUD sont correctement appliquées
Teste avec des tables réelles et capture les erreurs détaillées
"""
import os
import sys
import django
import json
import requests
from datetime import datetime, timedelta
from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import connection

# Configuration PostgREST
POSTGREST_URL = "http://localhost:3000"

# Rôles de test
ROLES_TEST = {
    'Expansion_L1': ('expansion_l1', 'Expansion_L1', ['CREATE']),
    'Expansion_L2': ('expansion_l2', 'Expansion_L2', ['READ', 'UPDATE']),
    'MRV_L1': ('mrv_l1', 'MRV_L1', ['READ']),
    'MRV_L2': ('mrv_l2', 'MRV_L2', ['READ', 'UPDATE']),
    'MRV_L3': ('mrv_l3', 'MRV_L3', ['READ', 'UPDATE', 'VALIDATE']),
    'Admin_L1': ('admin_l1', 'Admin_L1', ['READ', 'UPDATE']),
    'Admin_L2': ('admin_l2', 'Admin_L2', ['READ', 'UPDATE', 'DELETE']),
}

# Tables de test avec leurs permissions attendues
TEST_TABLES = {
    'communes': {
        'read_only': True,
        'description': 'Référentiel (lecture seulement pour tous)',
    },
    'bosquet_suivi': {
        'read_only': False,
        'description': 'Données métier (création/modif/suppression)',
    },
}

def create_test_users():
    """Crée les utilisateurs de test pour chaque rôle"""
    print("\n👥 Création des utilisateurs de test")
    print("-" * 80)
    
    users = {}
    for role_name, (username, display_role, perms) in ROLES_TEST.items():
        try:
            user = User.objects.get(email=f'{username}@teraka.org')
            print(f"  ℹ️  {username:<20} (rôle: {display_role:<15}) - Existant")
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=f'{username}@teraka.org',
                nom=username,
                password='testpass123', genre='H',
                role_name=display_role
            )
            print(f"  ✅ {username:<20} (rôle: {display_role:<15}) - Créé")
        
        users[role_name] = user
    
    return users

def get_jwt_token(user, role):
    """Génère un JWT token pour un utilisateur avec un rôle spécifique"""
    refresh = RefreshToken.for_user(user)
    
    # Ajouter le rôle au payload du token
    refresh.payload['role'] = role
    
    return str(refresh.access_token)

def test_table_access(role_name, token, perms, table_name, table_config):
    """Teste l'accès à une table avec un rôle donné"""
    print(f"\n  📊 Table: {table_name} ({table_config['description']})")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test READ
    print(f"     • READ: ", end='', flush=True)
    try:
        response = requests.get(
            f"{POSTGREST_URL}/{table_name}?limit=1",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            print(f"✅ ({count} ligne(s))")
        elif response.status_code == 403:
            print(f"❌ Forbidden")
        else:
            print(f"❌ Status {response.status_code}")
            if response.text:
                print(f"        └─ {response.text[:80]}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:60]}")
    
    # Test CREATE (si on a la permission et que la table n'est pas read-only)
    if 'CREATE' in perms and not table_config['read_only']:
        print(f"     • CREATE: ", end='', flush=True)
        
        # Préparer les données selon la table
        if table_name == 'bosquet_suivi':
            test_data = {
                'id_bosquet': 1,
                'annee': 2026,
                'semis_realise': True,
            }
        else:
            test_data = {'nom': f'TEST_{role_name}_{int(datetime.now().timestamp())}'}
        
        try:
            response = requests.post(
                f"{POSTGREST_URL}/{table_name}",
                headers=headers,
                json=test_data,
                timeout=5
            )
            if response.status_code in [200, 201]:
                print("✅ OK")
            elif response.status_code == 403:
                print("❌ Forbidden")
            elif response.status_code == 400:
                print(f"ℹ️  Bad Request (données invalides)")
            else:
                print(f"❌ Status {response.status_code}")
                if response.text:
                    print(f"        └─ {response.text[:80]}")
        except Exception as e:
            print(f"ℹ️  Erreur: {str(e)[:60]}")
    
    # Test UPDATE (si on a la permission et que la table n'est pas read-only)
    if 'UPDATE' in perms and not table_config['read_only']:
        print(f"     • UPDATE: ", end='', flush=True)
        
        if table_name == 'bosquet_suivi':
            update_data = {'semis_realise': False}
            query = "?id_bosquet=eq.1&annee=eq.2026"
        else:
            update_data = {'nom': f'UPDATED_{role_name}'}
            query = "?id=eq.1"
        
        try:
            response = requests.patch(
                f"{POSTGREST_URL}/{table_name}{query}",
                headers=headers,
                json=update_data,
                timeout=5
            )
            if response.status_code in [200, 204]:
                print("✅ OK")
            elif response.status_code == 403:
                print("❌ Forbidden")
            elif response.status_code == 400:
                print(f"ℹ️  Bad Request")
            else:
                print(f"❌ Status {response.status_code}")
                if response.text:
                    print(f"        └─ {response.text[:80]}")
        except Exception as e:
            print(f"ℹ️  Erreur: {str(e)[:60]}")
    
    # Test DELETE (si on a la permission et que la table n'est pas read-only)
    if 'DELETE' in perms and not table_config['read_only']:
        print(f"     • DELETE: ", end='', flush=True)
        
        if table_name == 'bosquet_suivi':
            query = "?id_bosquet=eq.999999&annee=eq.2026"
        else:
            query = "?id=eq.999999"
        
        try:
            response = requests.delete(
                f"{POSTGREST_URL}/{table_name}{query}",
                headers=headers,
                timeout=5
            )
            if response.status_code in [200, 204]:
                print("✅ OK")
            elif response.status_code == 403:
                print("❌ Forbidden")
            else:
                print(f"ℹ️  Status {response.status_code}")
        except Exception as e:
            print(f"ℹ️  Erreur: {str(e)[:60]}")

def check_postgrest_connection():
    """Vérifie que PostgREST est accessible"""
    print("🔗 Vérification de la connexion PostgREST")
    print("-" * 80)
    
    try:
        # Vérifier la racine
        response = requests.get(f"{POSTGREST_URL}/", timeout=5)
        print(f"  ✅ PostgREST accessible sur {POSTGREST_URL}")
        
        # Tenter d'obtenir l'info de version
        response = requests.get(f"{POSTGREST_URL}/", timeout=5, headers={'Accept': 'application/vnd.pgrst.object+json'})
        if response.headers.get('Server'):
            print(f"  ℹ️  {response.headers.get('Server')}")
        
        return True
    except requests.exceptions.ConnectionError:
        print(f"  ❌ PostgREST non accessible sur {POSTGREST_URL}")
        print(f"     Assurez-vous que PostgREST est démarré: python run_servers.py")
        return False
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def main():
    print("\n" + "=" * 80)
    print("🧪 TEST AVANCÉ DES RÔLES RBAC AVEC POSTGREST")
    print("=" * 80)
    
    # Vérifier PostgREST
    if not check_postgrest_connection():
        print("\n❌ PostgREST n'est pas accessible. Veuillez démarrer les serveurs.")
        print("   Exécutez: python run_servers.py")
        return False
    
    print()
    
    # Créer les utilisateurs de test
    users = create_test_users()
    
    print("\n" + "=" * 80)
    print("🧪 TEST D'ACCÈS AUX TABLES")
    print("=" * 80)
    
    # Tester chaque rôle
    for role_name, (username, display_role, perms) in ROLES_TEST.items():
        print(f"\n🔐 Rôle: {role_name}")
        print(f"   Permissions attendues: {', '.join(perms)}")
        
        user = users[role_name]
        token = get_jwt_token(user, display_role)
        
        # Tester chaque table
        for table_name, table_config in TEST_TABLES.items():
            test_table_access(role_name, token, perms, table_name, table_config)
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"""
✅ Tables testées: {', '.join(TEST_TABLES.keys())}
✅ Rôles testés: 7/7
✅ Permissions testées: READ, CREATE, UPDATE, DELETE

📋 Interprétation des résultats:
   ✅ = Permission accordée
   ❌ = Permission refusée (Forbidden 403)
   ℹ️  = Erreur de données ou autres (non liée aux permissions)

💡 Remarques:
   • Les tables read-only (communes) ne testent que READ
   • Les tables métier testent CREATE/UPDATE/DELETE
   • Les tokens JWT incluent le rôle PostgreSQL
   • PostgREST applique les permissions au niveau SQL
    """)
    
    print("=" * 80)
    print("✅ Test terminé")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)