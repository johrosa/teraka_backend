"""
Model pour associer les utilisateurs Django aux rôles PostgreSQL RBAC
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


DEFAULT_POSTGRES_ROLES = [
    ('Expansion_L1', 'Expansion L1 - Création seulement'),
    ('Expansion_L2', 'Expansion L2 - Lecture + Modification'),
    ('MRV_L1', 'MRV L1 - Lecture seule'),
    ('MRV_L2', 'MRV L2 - Lecture + Modification'),
    ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation'),
    ('Admin_L1', 'Admin L1 - Lecture + Modification'),
    ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression'),
]


class Role(models.Model):
    code = models.CharField(max_length=64, unique=True, verbose_name='Code du rôle')
    description = models.CharField(max_length=255, verbose_name='Description du rôle')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rôle PostgreSQL'
        verbose_name_plural = 'Rôles PostgreSQL'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.description}"

    @classmethod
    def ensure_default_roles(cls):
        for code, description in DEFAULT_POSTGRES_ROLES:
            cls.objects.get_or_create(code=code, defaults={'description': description})


class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        import uuid
        if 'uuid_user' not in extra_fields:
            extra_fields['uuid_user'] = uuid.uuid4()
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    uuid_user = models.UUIDField(unique=True, primary_key=True)
    operateur_id = models.TextField(blank=True, null=True)
    c_com = models.ForeignKey('core.Communes', models.DO_NOTHING, db_column='c_com', to_field='c_com', blank=True, null=True)
    nom = models.TextField()
    prenom = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    mot_de_passe = models.TextField(db_column='mot_de_passe')
    num_tel = models.TextField(unique=True, blank=True, null=True)
    annee_naissance = models.IntegerField(blank=True, null=True)
    genre = models.TextField(blank=True)  # Database has NOT NULL constraint
    adresse = models.TextField(blank=True, null=True)
    role_name = models.TextField(db_column='role', blank=True, null=True)
    photo = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom']

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.nom})"

    @property
    def password(self):
        return self.mot_de_passe

    @password.setter
    def password(self, value):
        self.mot_de_passe = value


class UserRole(models.Model):
    user = models.OneToOneField('core.Users', on_delete=models.CASCADE, related_name='postgres_role')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='user_roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Association Utilisateur-Rôle'
        verbose_name_plural = 'Associations Utilisateur-Rôle'
        ordering = ['user__email']


class FieldMapping(models.Model):
    model_name = models.CharField(max_length=128)
    field_name = models.CharField(max_length=128)
    source_field_name = models.CharField(max_length=128)
    comment = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Correspondance de champ'
        verbose_name_plural = 'Correspondances de champs'
        ordering = ['model_name', 'field_name']
        unique_together = ('model_name', 'field_name')

    @classmethod
    def load_mappings(cls):
        try:
            return {
                (mapping.model_name.lower(), mapping.field_name.lower()): mapping.source_field_name
                for mapping in cls.objects.filter(enabled=True)
            }
        except Exception:
            return {}
