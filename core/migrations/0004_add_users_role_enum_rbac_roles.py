from django.db import migrations, models


USER_ENUM_POSTGRES_ROLES = [
    ('ADMIN', 'Enum users.role ADMIN - full database access', 3),
    ('MRV', 'Enum users.role MRV - inherits from MRV_L3', 3),
    ('EXPANSION', 'Enum users.role EXPANSION - inherits from Expansion_L2', 2),
    ('OP_SAISIE', 'Enum users.role OP_SAISIE - inherits from Expansion_L1', 1),
    ('FINANCE', 'Enum users.role FINANCE - inherits from Admin_L1', 1),
    ('QUANTIFICATEUR', 'Enum users.role QUANTIFICATEUR - inherits from MRV_L2', 2),
]


def add_users_role_enum_rbac_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')

    for code, description, level in USER_ENUM_POSTGRES_ROLES:
        Role.objects.update_or_create(
            code=code,
            defaults={'description': description, 'level': level},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fieldmapping'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    ALTER TABLE core_role
                    ADD COLUMN IF NOT EXISTS level integer NOT NULL DEFAULT 0;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='role',
                    name='level',
                    field=models.IntegerField(default=0, verbose_name='Niveau'),
                ),
            ],
        ),
        migrations.RunPython(
            add_users_role_enum_rbac_roles,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
