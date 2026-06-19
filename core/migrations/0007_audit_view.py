from django.db import migrations

sql = r"""
CREATE OR REPLACE VIEW public.audit_log_view AS
SELECT
  a.id,
  a.event_time,
  a.schema_name,
  a.table_name,
  a.operation,
  a.row_data,
  a.changed_by,
  u.email AS changed_by_email,
  a.txid,
  a.prev_hash,
  a.row_hash
FROM public.audit_log a
LEFT JOIN public.users u ON u.uuid_user::text = a.changed_by;

COMMENT ON VIEW public.audit_log_view IS 'Readable view of audit_log with user email when available';
"""

reverse_sql = r"""
DROP VIEW IF EXISTS public.audit_log_view;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_userrole_options'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
