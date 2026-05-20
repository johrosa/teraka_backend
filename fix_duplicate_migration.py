#!/usr/bin/env python
"""
Script simple pour corriger le problème de migration sans besoin de Django
Exécutez avec: python fix_duplicate_migration.py
"""
import psycopg2
from psycopg2 import sql

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'database': 'teraka',
    'user': 'postgres',
    'password': 'postgres',  # Changez si nécessaire
}

print("=" * 80)
print("FIX: Migration UserRole en double")
print("=" * 80)

try:
    # Connexion à la base de données
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("\n1️⃣ Vérification de l'enregistrement de migration...")
    cursor.execute("""
        SELECT id, app, name, applied 
        FROM django_migrations 
        WHERE app = 'core' AND name LIKE '0002%'
        ORDER BY id DESC;
    """)

    migrations = cursor.fetchall()
    if migrations:
        print(f"Migrations trouvées: {len(migrations)}")
        for mid, app, name, applied in migrations:
            print(f"  - ID: {mid}, App: {app}, Name: {name}, Applied: {applied}")
    else:
        print("Aucune migration 0002 trouvée")

    # Supprimer l'enregistrement de migration 0002_userrole_auditlog
    print("\n2️⃣ Suppression de l'enregistrement de migration 0002_userrole_auditlog...")
    cursor.execute("""
        DELETE FROM django_migrations 
        WHERE app = 'core' AND name = '0002_userrole_auditlog';
    """)

    rows_deleted = cursor.rowcount
    print(f"✅ {rows_deleted} enregistrement(s) supprimé(s)")

    # Commiter les changements
    conn.commit()

    # Vérification finale
    print("\n3️⃣ Vérification des migrations restantes...")
    cursor.execute("""
        SELECT id, app, name, applied 
        FROM django_migrations 
        WHERE app = 'core'
        ORDER BY id DESC 
        LIMIT 5;
    """)

    print("Migrations actuelles de core:")
    for mid, app, name, applied in cursor.fetchall():
        print(f"  - ID: {mid}, App: {app}, Name: {name}, Applied: {applied}")

    # Vérifier la table
    print("\n4️⃣ Vérification de la table core_userrole...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'core_userrole'
        );
    """)

    if cursor.fetchone()[0]:
        print("✅ Table core_userrole existe")
    else:
        print("❌ Table core_userrole n'existe pas")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("✅ RÉPARATION TERMINÉE!")
    print("=" * 80)
    print("\nProchaine étape: Exécutez 'python manage.py migrate core'")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

