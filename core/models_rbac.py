"""
Model pour associer les utilisateurs Django aux rôles PostgreSQL RBAC
"""
from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    """
    Association entre un utilisateur Django et un rôle PostgreSQL
    Permet de contrôler les permissions de chaque utilisateur
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
    
    role = models.CharField(
        max_length=20,
        choices=POSTGRES_ROLES,
        verbose_name='Rôle PostgreSQL',
        help_text='Le rôle qui sera utilisé pour les permissions PostgREST'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Association Utilisateur-Rôle'
        verbose_name_plural = 'Associations Utilisateur-Rôle'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        """Override pour ajouter des traitements avant la sauvegarde"""
        super().save(*args, **kwargs)
