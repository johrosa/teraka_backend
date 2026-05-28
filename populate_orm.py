
import os
import django
import uuid
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Membre, PgInfos, ArbreBaseline, Users, Communes, BosquetGps, ArbreGps

def populate_data():
    print("Populating 10 rows of sample data via ORM...")

    # Get the admin user to use as operateur/verificateur
    admin = Users.objects.get(email='admin@teraka.org')
    # Get a valid commune
    commune = Communes.objects.first()

    for i in range(1, 11):
        # 1. PgInfos
        u_pg = uuid.uuid4()
        pg = PgInfos.objects.create(
            uuid_pg=u_pg,
            c_com=commune,
            date_saisie=datetime.now(timezone.utc),
            code_pg=f"PG-{i:03d}",
            nom_pg=f"Group {i}",
            date_inscription=datetime.now(timezone.utc),
            annee_inscription=2024,
            statut_pg="Validé",
            uuid_operateur=admin
        )

        # 2. Membre
        u_membre = uuid.uuid4()
        membre = Membre.objects.create(
            uuid_membre=u_membre,
            c_com=commune,
            date_saisie=datetime.now(timezone.utc),
            uuid_pg=pg,
            code_pg=f"PG-{i:03d}",
            nom_pg=f"Group {i}",
            statut_membre="Actif",
            date_statut=datetime.now(timezone.utc),
            nom_membre=f"Nom{i}",
            prenom_membre=f"Prenom{i}",
            genre="H",
            annee_inscription=2024,
            pepinieriste=False,
            leader=False,
            agent_cluster=False,
            quantificateur=False,
            deforestation=False,
            zone_riparienne=False,
            arbres_sup_10pct=False,
            uuid_operateur=admin
        )

        # 3. BosquetGps
        u_bosquet_gps = uuid.uuid4()
        bosquet_gps = BosquetGps.objects.create(
            uuid_bosquet_gps=u_bosquet_gps,
            uuid_membre=membre,
            uuid_pg=pg,
            c_com=commune,
            num_bosquet=str(i),
            code_bosquet=f"B-{i:03d}",
            statut_bosquet="Actif",
            date_statut=datetime.now(timezone.utc),
            date_creation=datetime.now(timezone.utc),
            geom='POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'
        )

        # 4. ArbreGps
        u_arbre_gps = uuid.uuid4()
        arbre_gps = ArbreGps.objects.create(
            uuid_arbre_gps=u_arbre_gps,
            operateur_id=str(admin.uuid_user),
            c_com=commune,
            uuid_bosquet_gps=bosquet_gps,
            geom='POINT(0 0)',
            numero_arbre=i,
            statut_arbre="Vivant"
        )

        # 5. ArbreBaseline
        u_arbre = uuid.uuid4()
        ArbreBaseline.objects.create(
            uuid_arbre_baseline=u_arbre,
            operateur_id=str(admin.uuid_user),
            c_com=commune,
            uuid_arbre_gps=arbre_gps, # Passing instance should work if to_field is not specified
            date_baseline=datetime.now(timezone.utc),
            age=5,
            annee_plantation=2019
        )

    print("Done populating 10 rows.")

if __name__ == "__main__":
    populate_data()
