"""
Model pour associer les utilisateurs Django aux rôles PostgreSQL RBAC
"""
from django.db import models
from django.contrib.auth.models import User, Group


class UserRole(models.Model):
    """
    Association entre un utilisateur Django et un rôle PostgreSQL
    Cette classe agit désormais comme un wrapper autour des groupes Django
    pour éviter de modifier la structure de la base de données.
    """
    
    POSTGRES_ROLES = [
        ('Expansion_L1', 'Expansion L1 - Création seulement'),
        ('Expansion_L2', 'Expansion L2 - Lecture + Modification'),
        ('MRV_L1', 'MRV L1 - Lecture seule'),
        ('MRV_L2', 'MRV L2 - Lecture + Modification'),
        ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation'),
        ('Admin_L1', 'Admin L1 - Lecture + Modification'),
        ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='postgres_role',
        verbose_name='Utilisateur Django'
    )
    
    # Le champ 'role' est supprimé du modèle de base de données pour éviter le ProgrammingError
    # Il est remplacé par une propriété dynamique qui interagit avec les groupes Django.
    
    @property
    def role(self):
        """Récupère le rôle depuis les groupes de l'utilisateur"""
        rbac_groups = [r[0] for r in self.POSTGRES_ROLES]
        user_group = self.user.groups.filter(name__in=rbac_groups).first()
        return user_group.name if user_group else None

    @role.setter
    def role(self, role_name):
        """Définit le rôle en gérant l'appartenance aux groupes Django"""
        rbac_groups = [r[0] for r in self.POSTGRES_ROLES]

        # Supprimer les anciens groupes RBAC
        self.user.groups.remove(*Group.objects.filter(name__in=rbac_groups))

        # Ajouter le nouveau groupe s'il est valide
        if role_name in rbac_groups:
            group, _ = Group.objects.get_or_create(name=role_name)
            self.user.groups.add(group)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Association Utilisateur-Rôle'
        verbose_name_plural = 'Associations Utilisateur-Rôle'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} ({self.role or 'Aucun rôle'})"
