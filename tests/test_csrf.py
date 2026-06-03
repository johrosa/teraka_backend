#!/usr/bin/env python
"""
Script de test rapide pour vérifier que l'import RBAC fonctionne
"""

import os
import sys
import django
from pathlib import Path

from _project_path import ensure_project_root

# Configuration Django
PROJECT_DIR = ensure_project_root()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_csrf_token():
    """Test que le token CSRF peut être généré"""
    from django.middleware.csrf import get_token
    from django.http import HttpRequest

    request = HttpRequest()
    request.session = {}

    try:
        token = get_token(request)
        print(f"✓ Token CSRF généré: {token[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur génération token CSRF: {e}")
        return False

def test_admin_templates():
    """Test que les templates admin sont accessibles"""
    from django.template.loader import get_template

    templates = [
        'admin/csv_form.html',
        'admin/rbac_change_list.html',
        'admin/base_site.html'
    ]

    for template_name in templates:
        try:
            template = get_template(template_name)
            print(f"✓ Template {template_name} accessible")
        except Exception as e:
            print(f"❌ Template {template_name} inaccessible: {e}")
            return False

    return True

def test_admin_view():
    """Test que la vue admin peut être instanciée"""
    from django.contrib import admin
    from core.admin import RBACAdmin
    from django.contrib.admin.sites import AdminSite

    try:
        site = AdminSite()
        admin_instance = RBACAdmin(admin.models.LogEntry, site)
        print("✓ RBACAdmin instancié correctement")
        return True
    except Exception as e:
        print(f"❌ Erreur instanciation RBACAdmin: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Test rapide CSRF et Admin")
    print("=" * 40)

    tests = [
        ("Token CSRF", test_csrf_token),
        ("Templates Admin", test_admin_templates),
        ("Vue Admin", test_admin_view),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔍 {name}:")
        result = test_func()
        results.append(result)

    print("\n" + "=" * 40)
    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        print("✅ Tous les tests passent!")
        print("\n💡 Essayez maintenant d'accéder à l'admin:")
        print("   http://localhost:8000/admin/")
        print("   → Allez dans LogEntry → 'Importer Matrice RBAC'")
        return 0
    else:
        print(f"❌ {total_count - success_count} test(s) échoué(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
