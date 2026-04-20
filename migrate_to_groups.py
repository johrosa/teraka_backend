#!/usr/bin/env python
"""
Script pour migrer du système UserRole vers les groupes Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models_rbac import UserRole

def migrate_to_groups():
    """Migrer les rôles vers des groupes Django"""
    print("Migration vers les groupes Django...")
    print()

    # Créer les groupes pour chaque rôle
    rbac_groups = {}
    for role_code, role_desc in UserRole.POSTGRES_ROLES:
        group, created = Group.objects.get_or_create(name=role_code)
        rbac_groups[role_code] = group
        if created:
            print(f"✓ Groupe créé: {role_code}")
        else:
            print(f"• Groupe existait déjà: {role_code}")

    print()

    # Assigner les utilisateurs aux groupes
    user_roles = UserRole.objects.select_related('user').all()

    for user_role in user_roles:
        user = user_role.user
        role = user_role.role

        # Vider les groupes existants
        user.groups.clear()

        # Assigner au nouveau groupe
        group = rbac_groups[role]
        user.groups.add(group)

        print(f"✓ {user.username} → groupe '{role}'")

    print()
    print(f"Migration terminée: {user_roles.count()} utilisateurs migrés")

    # Optionnel: supprimer le modèle UserRole
    # UserRole.objects.all().delete()
    # print("Modèle UserRole nettoyé")

if __name__ == '__main__':
    migrate_to_groups()
