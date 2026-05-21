from django.db import migrations, models
import django.db.models.deletion


def populate_user_role_fk(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    UserRole = apps.get_model('core', 'UserRole')

    default_roles = [
        ('Expansion_L1', 'Expansion L1 - Création seulement'),
        ('Expansion_L2', 'Expansion L2 - Lecture + Modification'),
        ('MRV_L1', 'MRV L1 - Lecture seule'),
        ('MRV_L2', 'MRV L2 - Lecture + Modification'),
        ('MRV_L3', 'MRV L3 - Lecture + Modification + Validation'),
        ('Admin_L1', 'Admin L1 - Lecture + Modification'),
        ('Admin_L2', 'Admin L2 - Lecture + Modification + Suppression'),
    ]

    for code, description in default_roles:
        Role.objects.get_or_create(code=code, defaults={'description': description})

    for user_role in UserRole.objects.all():
        role_code = getattr(user_role, 'role', None)
        if not role_code:
            continue

        role_obj, _ = Role.objects.get_or_create(
            code=role_code,
            defaults={'description': role_code}
        )
        user_role.role_fk_id = role_obj.pk
        user_role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_merge_0002_userrole_auditlog_0002b_userrole_safe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Identifiant unique du rôle PostgreSQL', max_length=64, unique=True, verbose_name='Code du rôle')),
                ('description', models.CharField(help_text='Description courte du rôle', max_length=255, verbose_name='Description du rôle')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
            ],
            options={
                'verbose_name': 'Rôle PostgreSQL',
                'verbose_name_plural': 'Rôles PostgreSQL',
                'ordering': ['code'],
            },
        ),
        migrations.AddField(
            model_name='userrole',
            name='role_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_roles', to='core.Role', verbose_name='Rôle PostgreSQL', help_text='Le rôle qui sera utilisé pour les permissions PostgREST'),
        ),
        migrations.RunPython(populate_user_role_fk, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='userrole',
            name='role',
        ),
        migrations.RenameField(
            model_name='userrole',
            old_name='role_fk',
            new_name='role',
        ),
        migrations.AlterField(
            model_name='userrole',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_roles', to='core.Role', verbose_name='Rôle PostgreSQL', help_text='Le rôle qui sera utilisé pour les permissions PostgREST'),
        ),
    ]
