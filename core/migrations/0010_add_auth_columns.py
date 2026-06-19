from django.db import migrations

sql = r"""
-- Ensure required auth fields exist on public.users for Django's auth machinery
ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS is_superuser boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_staff boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_active boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS last_login timestamptz,
  ADD COLUMN IF NOT EXISTS date_joined timestamptz;

-- Ensure NOT NULL where appropriate (only if column exists and is NULLABLE)
-- Set is_superuser/is_staff/is_active to not null with a default
ALTER TABLE public.users
  ALTER COLUMN is_superuser SET DEFAULT false,
  ALTER COLUMN is_staff SET DEFAULT false,
  ALTER COLUMN is_active SET DEFAULT true;

-- Optional: ensure boolean columns are NOT NULL
UPDATE public.users SET is_superuser = false WHERE is_superuser IS NULL;
UPDATE public.users SET is_staff = false WHERE is_staff IS NULL;
UPDATE public.users SET is_active = true WHERE is_active IS NULL;

ALTER TABLE public.users
  ALTER COLUMN is_superuser SET NOT NULL,
  ALTER COLUMN is_staff SET NOT NULL,
  ALTER COLUMN is_active SET NOT NULL;
"""

reverse_sql = r"""
ALTER TABLE public.users
  DROP COLUMN IF EXISTS date_joined,
  DROP COLUMN IF EXISTS last_login,
  DROP COLUMN IF EXISTS is_active,
  DROP COLUMN IF EXISTS is_staff,
  DROP COLUMN IF EXISTS is_superuser;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_add_is_superuser'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
