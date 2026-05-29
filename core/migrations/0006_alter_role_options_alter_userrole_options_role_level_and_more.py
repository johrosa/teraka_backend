from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_fieldmapping'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['code'], 'verbose_name': 'Rôle PostgreSQL', 'verbose_name_plural': 'Rôles PostgreSQL'},
        ),
        migrations.AlterModelOptions(
            name='userrole',
            options={'ordering': ['user__email'], 'verbose_name': 'Association Utilisateur-Rôle', 'verbose_name_plural': 'Associations Utilisateur-Rôle'},
        ),
        migrations.AddField(
            model_name='role',
            name='level',
            field=models.IntegerField(default=1, verbose_name='Niveau du rôle'),
        ),
    ]
