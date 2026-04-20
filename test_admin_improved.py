#!/usr/bin/env python
"""
Script de test pour l'interface admin améliorée
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models_rbac import UserRole

def test_admin_interface():
    """Tester les améliorations de l'interface admin"""

    print("🧪 TEST INTERFACE ADMIN AMÉLIORÉE")
    print("=" * 50)

    # Vérifier que les utilisateurs existent
    users_with_roles = User.objects.filter(postgres_role__isnull=False).select_related('postgres_role')
    print(f"✅ Utilisateurs avec rôles: {users_with_roles.count()}")

    for user in users_with_roles:
        print(f"  • {user.username} → {user.postgres_role.role}")

    print("\n📋 FONCTIONNALITÉS DISPONIBLES:")
    print("  • Dashboard Teraka: /admin/dashboard/")
    print("  • Gestion des rôles: /admin/core/userrole/")
    print("  • Import RBAC: /admin/core/logentry/rbac-status/")
    print("  • Statut RBAC: /admin/core/logentry/rbac-status/")

    print("\n🎨 AMÉLIORATIONS APPORTÉES:")
    print("  ✅ Dashboard avec statistiques en temps réel")
    print("  ✅ Interface UserRole améliorée avec descriptions")
    print("  ✅ Validation des rôles uniques par utilisateur")
    print("  ✅ Vue détaillée du statut RBAC")
    print("  ✅ Templates responsives et modernes")
    print("  ✅ Navigation améliorée")

    print("\n🔗 URLS À TESTER:")
    print("  1. http://localhost:8000/admin/dashboard/")
    print("  2. http://localhost:8000/admin/core/userrole/")
    print("  3. http://localhost:8000/admin/core/logentry/")
    print("  4. http://localhost:8000/admin/core/logentry/rbac-status/")

    print("\n📝 INSTRUCTIONS:")
    print("  • Connectez-vous avec un superuser (ex: django/admin)")
    print("  • Explorez le dashboard et les nouvelles fonctionnalités")
    print("  • Testez l'ajout/modification de rôles utilisateur")
    print("  • Vérifiez le statut des permissions RBAC")

if __name__ == '__main__':
    test_admin_interface()