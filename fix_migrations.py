#!/usr/bin/env python
"""
Script pour vérifier et appliquer les migrations manquantes
Usage: python fix_migrations.py
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command

print("=" * 80)
print("VÉRIFICATION ET APPLICATION DES MIGRATIONS")
print("=" * 80)

# 1. Afficher les migrations non appliquées
print("\n1️⃣ Affichage des migrations non appliquées:")
print("-" * 80)
call_command('showmigrations', 'core', verbosity=1)

# 2. Appliquer les migrations
print("\n2️⃣ Application des migrations:")
print("-" * 80)
try:
    call_command('migrate', 'core', verbosity=2)
    print("\n✅ Migrations appliquées avec succès!")
except Exception as e:
    print(f"\n❌ Erreur lors de l'application des migrations:")
    print(f"   {e}")
    sys.exit(1)

# 3. Vérifier que tout est bon
print("\n3️⃣ Vérification final:")
print("-" * 80)
from core.models_rbac import UserRole
from core.models import AuditLog

try:
    user_role_count = UserRole.objects.count()
    print(f"✅ Modèle UserRole accessible: {user_role_count} enregistrements")
except Exception as e:
    print(f"❌ Erreur accès UserRole: {e}")

try:
    audit_log_count = AuditLog.objects.count()
    print(f"✅ Modèle AuditLog accessible: {audit_log_count} enregistrements")
except Exception as e:
    print(f"❌ Erreur accès AuditLog: {e}")

print("\n" + "=" * 80)
print("FAIT!")
print("=" * 80)

