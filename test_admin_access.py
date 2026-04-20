#!/usr/bin/env python
"""
Test complet de l'interface admin Django
Vérifie que les rôles sont visibles et accessibles
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from core.models_rbac import UserRole

print("🧪 TEST COMPLET DE L'ADMIN DJANGO")
print("=" * 70)

# 1. Vérifier les utilisateurs avec rôles
print("\n1️⃣ VÉRIFICATION DES UTILISATEURS AVEC RÔLES")
print("-" * 70)

user_roles = UserRole.objects.select_related('user').all()
print(f"Total: {user_roles.count()} utilisateurs avec rôles\n")

for ur in user_roles:
    is_active = "✅" if ur.user.is_active else "❌"
    is_staff = "👤" if ur.user.is_staff else "  "
    print(f"{is_active} {is_staff} {ur.user.username:<20} → {ur.role:<15} (depuis {ur.created_at.strftime('%Y-%m-%d')})")

# 2. Vérifier l'accès admin
print("\n\n2️⃣ VÉRIFICATION DE L'ACCÈS ADMIN")
print("-" * 70)

client = Client()

# Vérifier qu'on peut accéder à la page de login
response = client.get('/admin/login/')
if response.status_code == 200:
    print("✅ Page de login admin accessible")
else:
    print(f"❌ Erreur lors de l'accès à /admin/login/ (Status: {response.status_code})")

# 3. Vérifier les superusers
print("\n\n3️⃣ VÉRIFICATION DES SUPERUSERS")
print("-" * 70)

superusers = User.objects.filter(is_superuser=True)
print(f"Total superusers: {superusers.count()}\n")

for superuser in superusers:
    print(f"  • {superuser.username}")
    print(f"    Email: {superuser.email}")
    print(f"    Staff: {superuser.is_staff}")
    print(f"    Actif: {superuser.is_active}")
    
    # Vérifier s'il a un rôle RBAC
    try:
        role = UserRole.objects.get(user=superuser)
        print(f"    Rôle RBAC: {role.role}")
    except UserRole.DoesNotExist:
        print(f"    Rôle RBAC: Aucun (utilisera 'postgres' par défaut)")
    print()

# 4. Informations sur l'interface admin
print("\n4️⃣ ACCÈS À L'INTERFACE ADMIN")
print("-" * 70)

print("🌐 URLs à tester:")
print("\n  1. Page de login:")
print("     http://localhost:8000/admin/login/")
print("\n  2. Accueil admin:")
print("     http://localhost:8000/admin/")
print("\n  3. Gestion des rôles (Associations Utilisateur-Rôle):")
print("     http://localhost:8000/admin/core/userrole/")
print("\n  4. Dashboard Teraka:")
print("     http://localhost:8000/admin/dashboard/")
print("\n  5. RBAC Import:")
print("     http://localhost:8000/admin/core/logentry/")

print("\n\n📝 ÉTAPES POUR ACCÉDER À L'ADMIN:")
print("-" * 70)
print("  1. Lancez Django: python manage.py runserver")
print("  2. Ouvrez: http://localhost:8000/admin/")
print("  3. Connectez-vous avec un superuser:")

for superuser in superusers:
    print(f"     • Utilisateur: {superuser.username}")
    print(f"     • Mot de passe: (utilisez le vôtre)")

print("\n  4. Une fois connecté, vous verrez:")
print("     • 'Associations Utilisateur-Rôle' dans le menu core")
print("     • Cliquez dessus pour voir la liste des rôles")
print("     • Les colonnes affichées: Utilisateur | Rôle | Description | Créé | Modifié | Actif")

print("\n\n✅ VÉRIFICATION COMPLÈTE TERMINÉE")
print("=" * 70)
