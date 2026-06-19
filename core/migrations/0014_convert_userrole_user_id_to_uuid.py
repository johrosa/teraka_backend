"""
Migration to convert core_userrole.user_id from bigint to uuid
and point FK to users.uuid_user instead of users.id

This fixes the "operator does not exist: bigint = uuid" error in the admin.
"""
from django.db import migrations


sql = r"""
-- Convert core_userrole.user_id from bigint to uuid, pointing to users.uuid_user

BEGIN;

  -- Step 1: Drop the old FK constraint
  ALTER TABLE core_userrole 
  DROP CONSTRAINT IF EXISTS core_userrole_user_id_aca63c51_fk_users_id;

  -- Step 2: Rename old column temporarily
  ALTER TABLE core_userrole 
  RENAME COLUMN user_id TO user_id_old;

  -- Step 3: Create new uuid column
  ALTER TABLE core_userrole 
  ADD COLUMN user_id uuid;

  -- Step 4: Backfill from users table using id -> uuid_user mapping
  UPDATE core_userrole ur
  SET user_id = u.uuid_user
  FROM users u
  WHERE ur.user_id_old = u.id;

  -- Step 5: Set NOT NULL constraint
  ALTER TABLE core_userrole 
  ALTER COLUMN user_id SET NOT NULL;

  -- Step 6: Drop old column
  ALTER TABLE core_userrole 
  DROP COLUMN user_id_old;

  -- Step 7: Create new FK constraint pointing to users.uuid_user
  ALTER TABLE core_userrole 
  ADD CONSTRAINT core_userrole_user_id_uuid_fk 
  FOREIGN KEY (user_id) REFERENCES users(uuid_user) 
  DEFERRABLE INITIALLY DEFERRED;

  -- Step 8: Create index for performance
  CREATE INDEX IF NOT EXISTS idx_core_userrole_user_id 
  ON core_userrole(user_id);

COMMIT;
"""

reverse_sql = r"""
-- Reverse is not implemented (would require preserving old bigint id mapping)
-- This is a one-way migration.
DO $$ BEGIN RAISE NOTICE 'Reverse of 0014_convert_userrole_user_id_to_uuid is a no-op'; END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_convert_fk_int_to_uuid'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
