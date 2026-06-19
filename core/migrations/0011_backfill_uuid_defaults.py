from django.db import migrations

sql = r"""
-- Ensure pgcrypto available for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- For every public table column named uuid_* with type uuid:
-- 1) set DEFAULT gen_random_uuid()
-- 2) fill NULLs with gen_random_uuid()
-- 3) set NOT NULL
DO $$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND column_name LIKE 'uuid_%'
      AND udt_name = 'uuid'
  LOOP
    BEGIN
      EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I SET DEFAULT gen_random_uuid();', r.table_name, r.column_name);
      EXECUTE format('UPDATE public.%I SET %I = gen_random_uuid() WHERE %I IS NULL;', r.table_name, r.column_name, r.column_name);
      EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I SET NOT NULL;', r.table_name, r.column_name);
    EXCEPTION WHEN others THEN
      RAISE NOTICE 'Skipping %:% due to: %', r.table_name, r.column_name, SQLERRM;
    END;
  END LOOP;
END;
$$;
"""

reverse_sql = r"""
-- Reverse: drop DEFAULT and allow NULLs again for uuid_* uuid columns
DO $$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND column_name LIKE 'uuid_%'
      AND udt_name = 'uuid'
  LOOP
    BEGIN
      EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I DROP DEFAULT;', r.table_name, r.column_name);
      EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I DROP NOT NULL;', r.table_name, r.column_name);
    EXCEPTION WHEN others THEN
      RAISE NOTICE 'Skipping reverse for %:% due to: %', r.table_name, r.column_name, SQLERRM;
    END;
  END LOOP;
END;
$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_auth_columns'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
