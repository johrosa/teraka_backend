# Generated migration to grant web_anon role permissions for PostgREST

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_convert_userrole_user_id_to_uuid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Grant web_anon role access to public schema and tables
            GRANT USAGE ON SCHEMA public TO web_anon;
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO web_anon;
            GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO web_anon;
            
            -- Make permissions apply to future tables created in public schema
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO web_anon;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO web_anon;
            """,
            reverse_sql="""
            -- Revoke permissions (note: this doesn't undo ALTER DEFAULT PRIVILEGES completely)
            REVOKE USAGE ON SCHEMA public FROM web_anon;
            REVOKE SELECT ON ALL TABLES IN SCHEMA public FROM web_anon;
            REVOKE SELECT ON ALL SEQUENCES IN SCHEMA public FROM web_anon;
            """
        ),
    ]
