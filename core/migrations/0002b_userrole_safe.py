"""
Migration alternative 0002b pour créer UserRole de manière sûre
Cette migration utilise RunSQL avec CREATE TABLE IF NOT EXISTS
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Créer la table avec CREATE TABLE IF NOT EXISTS pour éviter les doublons
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'core_userrole'
                ) THEN
                    CREATE TABLE core_userrole (
                        id BIGSERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
                        updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp
                    );
                    CREATE INDEX core_userrole_role_idx ON core_userrole(role);
                    CREATE INDEX core_userrole_user_id_idx ON core_userrole(user_id);
                END IF;
            END $$;
            """,
            reverse_sql="DROP TABLE IF EXISTS core_userrole CASCADE;",
        ),
    ]

