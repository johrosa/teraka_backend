"""
Model pour associer les utilisateurs Django aux rôles PostgreSQL RBAC
"""
from django.db import models
from django.conf import settings


BASE_POSTGRES_ROLES = [
    ('Expansion_L1', 'Expansion L1 - Création seulement', 1),
    ('Expansion_L2', 'Expansion L2 - Lecture + Modification', 2),
    ('MRV_L1', 'MRV L1 - Lecture seule', 1),
    ('MRV_L2', 'MRV L2 - Lecture + Modification', 2),
    ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation', 3),
    ('Admin_L1', 'Admin L1 - Lecture + Modification', 1),
    ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression', 2),
]

USER_ENUM_POSTGRES_ROLES = [
    ('ADMIN', 'Enum users.role ADMIN - full database access', 3),
    ('MRV', 'Enum users.role MRV - inherits from MRV_L3', 3),
    ('EXPANSION', 'Enum users.role EXPANSION - inherits from Expansion_L2', 2),
    ('OP_SAISIE', 'Enum users.role OP_SAISIE - inherits from Expansion_L1', 1),
    ('FINANCE', 'Enum users.role FINANCE - inherits from Admin_L1', 1),
    ('QUANTIFICATEUR', 'Enum users.role QUANTIFICATEUR - inherits from MRV_L2', 2),
]

USER_ROLE_PERMISSION_ALIASES = {
    'MRV': 'MRV_L3',
    'EXPANSION': 'Expansion_L2',
    'OP_SAISIE': 'Expansion_L1',
    'FINANCE': 'Admin_L1',
    'QUANTIFICATEUR': 'MRV_L2',
}

ADMIN_ALL_ACCESS_ROLES = {'ADMIN'}
DEFAULT_POSTGRES_ROLES = BASE_POSTGRES_ROLES + USER_ENUM_POSTGRES_ROLES
BASE_POSTGRES_ROLE_CODES = [code for code, _, _ in BASE_POSTGRES_ROLES]
DEFAULT_POSTGRES_ROLE_CODES = [code for code, _, _ in DEFAULT_POSTGRES_ROLES]
VALIDATOR_ROLES = {'MRV_L3', 'Admin_L1', 'Admin_L2', 'ADMIN', 'MRV'}


class Role(models.Model):
    """
    Rôle PostgreSQL stocké en base pour permettre l'ajout et la gestion dynamique.
    """

    code = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Code du rôle',
        help_text='Identifiant unique du rôle PostgreSQL'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Description du rôle',
        help_text='Description courte du rôle'
    )
    level = models.IntegerField(default=0, verbose_name='Niveau')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Rôle PostgreSQL'
        verbose_name_plural = 'Rôles PostgreSQL'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.description}"

    @classmethod
    def ensure_default_roles(cls):
        for code, description, level in DEFAULT_POSTGRES_ROLES:
            cls.objects.update_or_create(
                code=code,
                defaults={'description': description, 'level': level},
            )


class UserRole(models.Model):
    """
    Association entre un utilisateur Django et un rôle PostgreSQL
    Permet de contrôler les permissions de chaque utilisateur
    """

    POSTGRES_ROLES = DEFAULT_POSTGRES_ROLES
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='postgres_role',
        verbose_name='Utilisateur Django'
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='user_roles',
        verbose_name='Rôle PostgreSQL',
        help_text='Le rôle qui sera utilisé pour les permissions PostgREST'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        verbose_name = 'Association Utilisateur-Rôle'
        verbose_name_plural = 'Associations Utilisateur-Rôle'
        ordering = ['user__email']
    
    def __str__(self):
        return f"{self.user.username} ({self.role.code})"
    
    def save(self, *args, **kwargs):
        """Override pour ajouter des traitements avant la sauvegarde"""
        super().save(*args, **kwargs)


class FieldMapping(models.Model):
    """
    Correspondance manuelle entre un champ Django et un champ source QGIS.
    """

    model_name = models.CharField(
        max_length=128,
        verbose_name='Modèle Django',
        help_text='Nom du modèle Django source (ex: communes)'
    )
    field_name = models.CharField(
        max_length=128,
        verbose_name='Champ Django',
        help_text='Nom du champ dans le modèle Django'
    )
    source_field_name = models.CharField(
        max_length=128,
        verbose_name='Champ source QGIS',
        help_text='Nom du champ dans la source QGIS qui correspond'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Commentaire',
        help_text='Note explicative sur la correspondance'
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Activer ou désactiver cette correspondance'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')

    class Meta:
        verbose_name = 'Correspondance de champ'
        verbose_name_plural = 'Correspondances de champs'
        ordering = ['model_name', 'field_name']
        unique_together = ('model_name', 'field_name')

    def __str__(self):
        return f"{self.model_name}.{self.field_name} → {self.source_field_name}"

    @classmethod
    def load_mappings(cls):
        return {
            (mapping.model_name.lower(), mapping.field_name.lower()): mapping.source_field_name
            for mapping in cls.objects.filter(enabled=True)
        }
