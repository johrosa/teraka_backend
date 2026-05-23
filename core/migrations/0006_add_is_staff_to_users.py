from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_fieldmapping'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users ADD COLUMN is_staff BOOLEAN NOT NULL DEFAULT FALSE;",
            reverse_sql="ALTER TABLE users DROP COLUMN is_staff;",
        ),
    ]
