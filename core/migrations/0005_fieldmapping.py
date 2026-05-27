from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_role_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(help_text='Nom du modèle Django source (ex: communes)', max_length=128, verbose_name='Modèle Django')),
                ('field_name', models.CharField(help_text='Nom du champ dans le modèle Django', max_length=128, verbose_name='Champ Django')),
                ('source_field_name', models.CharField(help_text='Nom du champ dans la source QGIS qui correspond', max_length=128, verbose_name='Champ source QGIS')),
                ('comment', models.TextField(blank=True, null=True, help_text='Note explicative sur la correspondance', verbose_name='Commentaire')),
                ('enabled', models.BooleanField(default=True, help_text='Activer ou désactiver cette correspondance', verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
            ],
            options={
                'verbose_name': 'Correspondance de champ',
                'verbose_name_plural': 'Correspondances de champs',
                'ordering': ['model_name', 'field_name'],
                'unique_together': {('model_name', 'field_name')},
            },
        ),
    ]
