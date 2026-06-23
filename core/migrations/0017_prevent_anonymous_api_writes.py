"""Prevent unauthenticated PostgREST writes through the web_anon role."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_capture_jwt_user_in_audit_log'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM web_anon;
            REVOKE USAGE, UPDATE ON ALL SEQUENCES IN SCHEMA public FROM web_anon;

            ALTER DEFAULT PRIVILEGES IN SCHEMA public
                REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON TABLES FROM web_anon;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
                REVOKE USAGE, UPDATE ON SEQUENCES FROM web_anon;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
