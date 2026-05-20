#!/usr/bin/env python
"""
Script pour corriger l'état des migrations
Exécutez ceci: python fix_migration.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from django.db import connection

print("=" * 80)
print("CORRECTION DE L'ÉTAT DES MIGRATIONS")
print("=" * 80)

# 1. Vérifier si la table existe
print("\n1️⃣ Vérification de la table core_userrole...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'core_userrole'
        );
    """)
    table_exists = cursor.fetchone()[0]

if table_exists:
    print("✅ Table core_userrole existe en base de données")
else:
    print("❌ Table core_userrole N'existe PAS")

# 2. Vérifier l'état des migrations
print("\n2️⃣ État des migrations...")
try:
    call_command('showmigrations', 'core', verbosity=1)
except Exception as e:
    print(f"Erreur: {e}")

# 3. Fake la migration 0002 si la table existe
if table_exists:
    print("\n3️⃣ Marquage de la migration 0002 comme appliquée (table existe déjà)...")
    try:
        call_command('migrate', 'core', '0002_userrole_auditlog', fake=True, verbosity=2)
        print("✅ Migration 0002 marquée comme appliquée")
    except Exception as e:
        print(f"⚠️  Erreur: {e}")

# 4. Appliquer toutes les migrations
print("\n4️⃣ Application des migrations...")
try:
    call_command('migrate', 'core', verbosity=2)
    print("✅ Toutes les migrations appliquées")
except Exception as e:
    print(f"❌ Erreur: {e}")

# 5. Vérification finale
print("\n5️⃣ Vérification finale...")
try:
    from core.models import UserRole
    count = UserRole.objects.count()
    print(f"✅ Modèle UserRole accessible: {count} enregistrements")
except Exception as e:
    print(f"❌ Erreur accès UserRole: {e}")

print("\n" + "=" * 80)
print("TERMINÉ!")
print("=" * 80)

