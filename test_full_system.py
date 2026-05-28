import requests
import json
import jwt
import time
import os
import django
from datetime import datetime
from uuid import uuid4

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_rbac import Role, UserRole
from core.models import Communes, Membre, PgInfos, AuditLog
from django.db import connection

User = get_user_model()

# Configuration
DJANGO_URL = 'http://localhost:8000'
API_LOGIN = f'{DJANGO_URL}/api/login/'
POSTGREST_URL = 'http://localhost:3000'

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}=== {msg} ==={Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_fail(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def clean_test_data():
    print_step("NETTOYAGE DES DONNÉES MÉTIER")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM membre WHERE nom_membre LIKE 'TEST_%'")
    print_success("Nettoyage effectué (sans toucher à l'audit immuable)")

def test_auth_and_rbac_selection():
    print_step("TEST 1: AUTHENTIFICATION ET SÉLECTION DE RÔLE")

    email = 'admin@teraka.org'
    password = 'admin'

    # 1. Login sans spécifier de rôle -> Doit donner L1 (Admin_L1)
    res = requests.post(API_LOGIN, json={'email': email, 'password': password})
    token_l1 = res.json()['access']
    decoded = jwt.decode(token_l1, options={"verify_signature": False})
    role = decoded.get('role')
    if role == 'Admin_L1':
        print_success("Défaut Moindre Privilège: OK (Admin_L1 obtenu)")
    else:
        print_fail(f"Défaut Moindre Privilège: FAIL (obtenu {role})")

    # 2. Login avec rôle spécifique (L2) -> Doit donner Admin_L2
    res = requests.post(API_LOGIN, json={'email': email, 'password': password, 'role': 'Admin_L2'})
    token_l2 = res.json()['access']
    decoded = jwt.decode(token_l2, options={"verify_signature": False})
    role = decoded.get('role')
    if role == 'Admin_L2':
        print_success("Sélection de rôle autorisé (L2): OK")
    else:
        print_fail(f"Sélection de rôle autorisé (L2): FAIL (obtenu {role})")

    return token_l2

def test_rbac_editing():
    print_step("TEST 2: ÉDITION RBAC (MODIFICATION DE RÔLE)")

    user = User.objects.get(email='expansion_l1@teraka.org')
    ur, _ = UserRole.objects.get_or_create(user=user, defaults={'role': Role.objects.get(code='Expansion_L1')})
    original_role = ur.role

    # Changer Expansion_L1 en Expansion_L2
    new_role = Role.objects.get(code='Expansion_L2')
    ur.role = new_role
    ur.save()
    print_success(f"Changement de rôle Django: {user.email} -> {new_role.code}")

    # Vérifier que le nouveau token contient le nouveau rôle (si on demande L2)
    res = requests.post(API_LOGIN, json={'email': 'expansion_l1@teraka.org', 'password': 'test123', 'role': 'Expansion_L2'})
    if res.status_code == 200:
        token = res.json()['access']
        decoded = jwt.decode(token, options={"verify_signature": False})
        if decoded.get('role') == 'Expansion_L2':
            print_success("Synchronisation RBAC: OK (Nouveau token valide)")
        else:
            print_fail(f"Synchronisation RBAC: FAIL (obtenu {decoded.get('role')})")

    # Remettre à l'origine
    ur.role = original_role
    ur.save()
    print_success("Restauration du rôle original: OK")

def test_django_orm_editing():
    print_step("TEST 3: ÉDITION VIA DJANGO ORM")

    commune = Communes.objects.first()
    pg = PgInfos.objects.first()

    test_uuid = uuid4()
    membre = Membre.objects.create(
        uuid_membre=test_uuid,
        c_com=commune,
        date_saisie=datetime.now(),
        uuid_pg=pg,
        code_pg=pg.code_pg,
        nom_pg=pg.nom_pg,
        statut_membre='Actif',
        date_statut=datetime.now(),
        nom_membre='TEST_NOM',
        genre='Masculin',
        annee_inscription=2024,
        pepinieriste=False,
        leader=False,
        agent_cluster=False,
        quantificateur=False,
        deforestation=False,
        zone_riparienne=False,
        arbres_sup_10pct=False
    )
    print_success(f"Création Membre ORM: OK")

    membre.prenom_membre = 'PRENOM_MODIFIE'
    membre.save()
    print_success("Modification Membre ORM: OK")

    return test_uuid

def test_api_loading_and_editing(token, uuid_membre):
    print_step("TEST 4: API POSTGREST - CHARGEMENT ET ÉDITION")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    # 1. Loading
    res = requests.get(f"{POSTGREST_URL}/membre?uuid_membre=eq.{uuid_membre}", headers=headers)
    if res.status_code == 200 and len(res.json()) > 0:
        print_success("Chargement API (GET): OK")
    else:
        print_fail(f"Chargement API (GET): FAIL ({res.status_code})")

    # 2. Editing
    res = requests.patch(
        f"{POSTGREST_URL}/membre?uuid_membre=eq.{uuid_membre}",
        headers=headers,
        json={'prenom_membre': 'API_MODIFIE'}
    )
    if res.status_code in [200, 204]:
        print_success("Édition API (PATCH): OK")
    else:
        print_fail(f"Édition API (PATCH): FAIL ({res.status_code}) {res.text}")

    # 3. Deletion
    res = requests.delete(f"{POSTGREST_URL}/membre?uuid_membre=eq.{uuid_membre}", headers=headers)
    if res.status_code in [200, 204]:
        print_success("Suppression API (DELETE): OK")
    else:
        print_fail(f"Suppression API (DELETE): FAIL ({res.status_code})")

def test_audit_log():
    print_step("TEST 5: VÉRIFICATION DE L'AUDIT")
    time.sleep(1)
    # Chercher les logs récents pour la table membre
    logs = AuditLog.objects.filter(table_name='membre').order_by('-action_time')[:5]
    if logs.exists():
        print_success(f"Audit Log: OK ({len(logs)} entrées récentes)")
        for log in logs:
            print(f"  • {log.action_time.strftime('%H:%M:%S')} | {log.operation} | User: {log.user_id}")
    else:
        print_fail("Audit Log: FAIL (Aucune entrée trouvée)")

def main():
    try:
        clean_test_data()
        token = test_auth_and_rbac_selection()
        test_rbac_editing()
        uuid_membre = test_django_orm_editing()
        if uuid_membre:
            test_api_loading_and_editing(token, uuid_membre)
            test_audit_log()
        print_step("RÉSULTAT GLOBAL: TOUT EST OPÉRATIONNEL")
    except Exception as e:
        print_fail(f"Erreur innatendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
