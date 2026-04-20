#!/usr/bin/env python
"""
Script pour vérifier l'enregistrement des modèles dans l'admin Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib import admin
from core.models_rbac import UserRole

print("🔍 VÉRIFICATION DE L'ENREGISTREMENT ADMIN")
print("=" * 60)

# Vérifier que UserRole est enregistré
if UserRole in admin.site._registry:
    print("✅ UserRole est enregistré dans l'admin")
    admin_class = admin.site._registry[UserRole]
    print(f"   Classe admin: {admin_class.__class__.__name__}")
    print(f"   list_display: {admin_class.list_display}")
else:
    print("❌ UserRole n'est PAS enregistré dans l'admin")
    print("   Modèles enregistrés:")
    for model in admin.site._registry.keys():
        if 'role' in model.__name__.lower() or 'user' in model.__name__.lower():
            print(f"      • {model.__name__}")

print("\n📋 MODÈLES ENREGISTRÉS (total: {})".format(len(admin.site._registry)))
print("-" * 60)

registered_apps = {}
for model in admin.site._registry.keys():
    app_name = model._meta.app_label
    if app_name not in registered_apps:
        registered_apps[app_name] = []
    registered_apps[app_name].append(model.__name__)

for app, models in sorted(registered_apps.items()):
    print(f"\n{app}:")
    for model in sorted(models):
        print(f"  • {model}")

print("\n🌐 URL ADMIN")
print("-" * 60)
print("Accédez à: http://localhost:8000/admin/")
print("Puis cliquez sur 'Associations Utilisateur-Rôle' pour voir les rôles")
