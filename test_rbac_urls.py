#!/usr/bin/env python
"""
Test des URLs RBAC autonomes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import resolve, reverse
from django.test import Client

print("🔍 TEST DES URLS RBAC AUTONOMES")
print("=" * 70)

# 1. Tester que les URLs existent
print("\n1️⃣ VÉRIFICATION DES URLS")
print("-" * 70)

urls_to_test = [
    ('rbac_import', '/admin/rbac/import/'),
    ('rbac_status', '/admin/rbac/status/'),
]

for url_name, url_path in urls_to_test:
    try:
        resolved = resolve(url_path)
        print(f"✅ {url_name}: {url_path}")
        print(f"   View: {resolved.func.__name__}")
        print(f"   Pattern name: {resolved.url_name}")
    except Exception as e:
        print(f"❌ {url_name}: {url_path}")
        print(f"   Erreur: {e}")

# 2. Tester l'accès aux URLs
print("\n\n2️⃣ VÉRIFICATION DE L'ACCÈS AUX URLS")
print("-" * 70)

client = Client()

for url_name, url_path in urls_to_test:
    try:
        # Tester sans authentification (devrait rediriger vers login)
        response = client.get(url_path)
        if response.status_code == 302:
            print(f"✅ {url_path}: Redirection vers login (attendu)")
            print(f"   Status: {response.status_code}")
            print(f"   Redirect to: {response.url}")
        elif response.status_code == 200:
            print(f"✅ {url_path}: Accessible sans authentification")
            print(f"   Status: {response.status_code}")
        else:
            print(f"⚠️  {url_path}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ {url_path}: Erreur")
        print(f"   {e}")

# 3. Afficher les URLs générées par reverse
print("\n\n3️⃣ VÉRIFICATION AVEC reverse()")
print("-" * 70)

try:
    import_url = reverse('rbac_import')
    status_url = reverse('rbac_status')
    
    print(f"✅ Import URL: {import_url}")
    print(f"✅ Status URL: {status_url}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# 4. Résumé
print("\n\n4️⃣ RÉSUMÉ")
print("-" * 70)

print("🌐 URLs RBAC Autonomes:")
print("  • Import: http://localhost:8000/admin/rbac/import/")
print("  • Status: http://localhost:8000/admin/rbac/status/")
print("  • Gestion des rôles: http://localhost:8000/admin/core/userrole/")

print("\n✅ Test terminé")
