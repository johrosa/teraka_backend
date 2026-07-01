"""Archive bosquet_gps geometry changes in bosquet_geom_historique."""
from django.db import migrations


sql = r"""
CREATE OR REPLACE FUNCTION public.archive_bosquet_gps_geom_change()
RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.geom IS NOT NULL
       AND NEW.geom IS NOT NULL
       AND NOT ST_Equals(OLD.geom, NEW.geom)
    THEN
        INSERT INTO public.bosquet_geom_historique (
            uuid_bosquet_geom_historique,
            geom,
            uuid_bosquet_gps,
            uuid_operateur,
            uuid_verificateur,
            area_ha,
            date,
            source
        )
        VALUES (
            gen_random_uuid(),
            OLD.geom,
            OLD.uuid_bosquet_gps,
            COALESCE(OLD.uuid_operateur, NEW.uuid_operateur),
            COALESCE(OLD.uuid_verificateur, NEW.uuid_verificateur),
            OLD.area_ha,
            CURRENT_TIMESTAMP,
            'server_geom_trigger'
        );
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_archive_bosquet_gps_geom_change ON public.bosquet_gps;

CREATE TRIGGER trg_archive_bosquet_gps_geom_change
BEFORE UPDATE OF geom ON public.bosquet_gps
FOR EACH ROW
EXECUTE FUNCTION public.archive_bosquet_gps_geom_change();
"""


reverse_sql = r"""
DROP TRIGGER IF EXISTS trg_archive_bosquet_gps_geom_change ON public.bosquet_gps;
DROP FUNCTION IF EXISTS public.archive_bosquet_gps_geom_change();
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_prevent_anonymous_api_writes'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
    ]
