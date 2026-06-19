from django.db import migrations

sql = r"""
-- Add is_superuser boolean column to users table if missing
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS is_superuser boolean DEFAULT false;
"""

reverse_sql = r"""
-- Remove is_superuser column if reversing
ALTER TABLE public.users DROP COLUMN IF EXISTS is_superuser;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_add_last_login'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
