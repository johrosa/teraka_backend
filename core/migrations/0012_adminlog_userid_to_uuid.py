from django.db import migrations

sql = r"""
-- Migrate django_admin_log.user_id from bigint referencing users.id to uuid referencing users.uuid_user
-- Safe steps: create new uuid column, copy mapped uuids, drop old column, rename new column, add FK

BEGIN;

-- Drop existing FK if present
ALTER TABLE public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;

-- Add temporary uuid column
ALTER TABLE public.django_admin_log ADD COLUMN IF NOT EXISTS user_uuid uuid;

-- Populate user_uuid by joining on users.id -> users.uuid_user
UPDATE public.django_admin_log dal
SET user_uuid = u.uuid_user
FROM public.users u
WHERE dal.user_id::text = u.id::text OR dal.user_id = u.id;

-- Drop old integer user_id column
ALTER TABLE public.django_admin_log DROP COLUMN IF EXISTS user_id;

-- Rename temp column to user_id
ALTER TABLE public.django_admin_log RENAME COLUMN user_uuid TO user_id;

-- Add FK to users(uuid_user)
ALTER TABLE public.django_admin_log
  ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (uuid_user) DEFERRABLE INITIALLY DEFERRED;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_django_admin_log_user_id ON public.django_admin_log (user_id);

COMMIT;
"""

reverse_sql = r"""
-- Reverse migration is not automatic: restoring integer IDs from UUIDs may be lossy.
-- We leave a no-op reverse that raises a notice.
DO $$
BEGIN
  RAISE NOTICE 'Reverse of 0012_adminlog_userid_to_uuid is a no-op.';
END;
$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_backfill_uuid_defaults'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
