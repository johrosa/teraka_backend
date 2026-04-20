#!/usr/bin/env python
"""
Script pour réinitialiser les mots de passe des utilisateurs RBAC à 'test123'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Utilisateurs RBAC
rbac_users = [
    'expansion_l1',
    'expansion_l2', 
    'mrv_l1',
    'mrv_l2',
    'mrv_l3',
    'admin_l1',
    'admin_l2',
]

print("Réinitialisation des mots de passe...")
print()

for username in rbac_users:
    try:
        user = User.objects.get(username=username)
        user.set_password('test123')
        user.save()
        print(f"✓ {username}: mot de passe réinitialisé")
    except User.DoesNotExist:
        print(f"✗ {username}: utilisateur non trouvé")
    except Exception as e:
        print(f"✗ {username}: erreur - {e}")

print()
print("Tous les utilisateurs peuvent maintenant se connecter avec le mot de passe 'test123'")
