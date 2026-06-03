#!/usr/bin/env python
"""
Comparaison entre UserRole (modèle personnalisé) et Group (groupes Django)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models_rbac import UserRole

def compare_approaches():
    """Comparer les deux approches de gestion des rôles"""

    print("="*80)
    print("COMPARAISON: UserRole vs Groupes Django")
    print("="*80)
    print()

    # 1. Compter les utilisateurs avec rôles
    user_roles_count = UserRole.objects.count()
    users_with_groups = User.objects.filter(groups__name__in=[
        'Expansion_L1', 'Expansion_L2', 'MRV_L1', 'MRV_L2', 'MRV_L3', 'Admin_L1', 'Admin_L2'
    ]).distinct().count()

    print("📊 STATISTIQUES ACTUELLES:")
    print(f"  • Utilisateurs avec UserRole: {user_roles_count}")
    print(f"  • Utilisateurs dans groupes RBAC: {users_with_groups}")
    print()

    # 2. Avantages UserRole
    print("✅ AVANTAGES UserRole (modèle personnalisé):")
    print("  • Sémantique claire: un rôle = une responsabilité")
    print("  • Contrôle strict: un utilisateur = un rôle")
    print("  • Interface admin dédiée et intuitive")
    print("  • Audit trail (created_at/updated_at)")
    print("  • Pas de confusion avec permissions Django")
    print("  • Performance: requête directe, pas de jointures")
    print()

    # 3. Avantages Groupes
    print("✅ AVANTAGES Groupes Django:")
    print("  • Intégration native avec Django")
    print("  • Flexibilité: utilisateur peut avoir plusieurs rôles")
    print("  • Permissions Django + rôles SQL possibles")
    print("  • Interface admin Django standard")
    print("  • Moins de code personnalisé à maintenir")
    print()

    # 4. Inconvénients UserRole
    print("❌ INCONVÉNIENTS UserRole:")
    print("  • Code personnalisé à maintenir")
    print("  • Migration nécessaire si changement d'approche")
    print("  • Interface admin séparée des groupes Django")
    print()

    # 5. Inconvénients Groupes
    print("❌ INCONVÉNIENTS Groupes Django:")
    print("  • Confusion potentielle entre permissions Django et rôles SQL")
    print("  • Plus de requêtes (jointure groups)")
    print("  • Interface moins intuitive pour 'un rôle par utilisateur'")
    print("  • Groupes conçus pour permissions objet, pas rôles SQL")
    print()

    # 6. Recommandation
    print("🎯 RECOMMANDATION:")
    print("  Pour votre cas d'usage RBAC avec PostgREST:")
    print("  → UserRole est PLUS APPROPRIÉ")
    print()
    print("  Pourquoi?")
    print("  • Vos rôles sont mutuellement exclusifs")
    print("  • Permissions gérées au niveau SQL, pas Django")
    print("  • Interface claire et directe")
    print("  • Performance optimale")
    print()

    # 7. Migration si souhaité
    print("🔄 MIGRATION POSSIBLE:")
    print("  Si vous voulez tester les groupes:")
    print("  1. python migrate_to_groups.py")
    print("  2. Modifier serializers.py pour importer serializers_groups")
    print("  3. Tester avec tests/test_end_to_end.py")
    print()

if __name__ == '__main__':
    compare_approaches()
