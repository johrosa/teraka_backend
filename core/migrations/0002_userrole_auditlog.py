"""
Migration pour ajouter UserRole et AuditLog
Note: La table core_userrole peut déjà exister, dans ce cas la migration fake cette opération
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Créer le modèle UserRole (migration sans action si table existe)
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[
                        ('Expansion_L1', 'Expansion L1 - Création seulement'),
                        ('Expansion_L2', 'Expansion L2 - Lecture + Modification'),
                        ('MRV_L1', 'MRV L1 - Lecture seule'),
                        ('MRV_L2', 'MRV L2 - Lecture + Modification'),
                        ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation'),
                        ('Admin_L1', 'Admin L1 - Lecture + Modification'),
                        ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression'),
                    ],
                    help_text='Le rôle qui sera utilisé pour les permissions PostgREST',
                    max_length=20,
                    verbose_name='Rôle PostgreSQL'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='postgres_role',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur Django'
                )),
            ],
            options={
                'verbose_name': 'Association Utilisateur-Rôle',
                'verbose_name_plural': 'Associations Utilisateur-Rôle',
                'ordering': ['user__username'],
                'managed': True,
            },
        ),
    ]