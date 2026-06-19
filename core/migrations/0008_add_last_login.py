from django.db import migrations

sql = r"""
-- Add nullable last_login timestamp column to users table if missing
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS last_login timestamptz;
"""

reverse_sql = r"""
-- Remove last_login column if reversing
ALTER TABLE public.users DROP COLUMN IF EXISTS last_login;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_audit_view'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
