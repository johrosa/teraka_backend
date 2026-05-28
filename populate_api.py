
import requests
import uuid
from datetime import datetime, timezone

def populate_api():
    print("Populating 10 rows of sample data via API...")

    # 1. Login to get JWT token
    login_url = "http://localhost:8000/api/login/"
    credentials = {
        "email": "admin@teraka.org",
        "password": "admin"
    }

    response = requests.post(login_url, json=credentials)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return

    token = response.json()["access"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Base URL for PostgREST
    postgrest_url = "http://localhost:3000"

    # Get a valid commune
    c_response = requests.get(f"{postgrest_url}/communes?limit=1", headers=headers)
    commune_id = c_response.json()[0]["c_com"]

    # Get user UUID
    u_response = requests.get(f"{postgrest_url}/users?email=eq.admin@teraka.org", headers=headers)
    admin_uuid = u_response.json()[0]["uuid_user"]

    for i in range(11, 21):
        print(f"Adding row {i}...")
        # 1. PgInfos
        u_pg = str(uuid.uuid4())
        pg_data = {
            "uuid_pg": u_pg,
            "c_com": commune_id,
            "date_saisie": datetime.now(timezone.utc).isoformat(),
            "code_pg": f"PG-{i:03d}",
            "nom_pg": f"Group {i}",
            "date_inscription": datetime.now(timezone.utc).isoformat(),
            "annee_inscription": 2024,
            "statut_pg": "Validé",
            "uuid_operateur": admin_uuid
        }
        r = requests.post(f"{postgrest_url}/pg_infos", json=pg_data, headers=headers)
        if r.status_code not in [200, 201]: print(f"Error pg_infos: {r.text}")

        # 2. Membre
        u_membre = str(uuid.uuid4())
        membre_data = {
            "uuid_membre": u_membre,
            "c_com": commune_id,
            "date_saisie": datetime.now(timezone.utc).isoformat(),
            "uuid_pg": u_pg,
            "code_pg": f"PG-{i:03d}",
            "nom_pg": f"Group {i}",
            "statut_membre": "Actif",
            "date_statut": datetime.now(timezone.utc).isoformat(),
            "nom_membre": f"Nom{i}",
            "prenom_membre": f"Prenom{i}",
            "genre": "H",
            "annee_inscription": 2024,
            "pepinieriste": False,
            "leader": False,
            "agent_cluster": False,
            "quantificateur": False,
            "deforestation": False,
            "zone_riparienne": False,
            "arbres_sup_10pct": False,
            "uuid_operateur": admin_uuid
        }
        r = requests.post(f"{postgrest_url}/membre", json=membre_data, headers=headers)
        if r.status_code not in [200, 201]: print(f"Error membre: {r.text}")

        # 3. BosquetGps
        u_bosquet_gps = str(uuid.uuid4())
        bosquet_data = {
            "uuid_bosquet_gps": u_bosquet_gps,
            "uuid_membre": u_membre,
            "uuid_pg": u_pg,
            "c_com": commune_id,
            "num_bosquet": str(i),
            "code_bosquet": f"B-{i:03d}",
            "statut_bosquet": "Actif",
            "date_statut": datetime.now(timezone.utc).isoformat(),
            "date_creation": datetime.now(timezone.utc).isoformat(),
            "geom": "SRID=32738;POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
        }
        r = requests.post(f"{postgrest_url}/bosquet_gps", json=bosquet_data, headers=headers)
        if r.status_code not in [200, 201]: print(f"Error bosquet_gps: {r.text}")

        # 4. ArbreGps
        u_arbre_gps = str(uuid.uuid4())
        arbre_gps_data = {
            "uuid_arbre_gps": u_arbre_gps,
            "operateur_id": admin_uuid,
            "c_com": commune_id,
            "uuid_bosquet_gps": u_bosquet_gps,
            "geom": "SRID=32738;POINT(0 0)",
            "numero_arbre": i,
            "statut_arbre": "Vivant"
        }
        r = requests.post(f"{postgrest_url}/arbre_gps", json=arbre_gps_data, headers=headers)
        if r.status_code not in [200, 201]: print(f"Error arbre_gps: {r.text}")

        # 5. ArbreBaseline
        u_arbre = str(uuid.uuid4())
        arbre_data = {
            "uuid_arbre_baseline": u_arbre,
            "operateur_id": admin_uuid,
            "c_com": commune_id,
            "uuid_arbre_gps": u_arbre_gps,
            "date_baseline": datetime.now(timezone.utc).isoformat(),
            "age": 5,
            "annee_plantation": 2019
        }
        r = requests.post(f"{postgrest_url}/arbre_baseline", json=arbre_data, headers=headers)
        if r.status_code not in [200, 201]: print(f"Error arbre_baseline: {r.text}")

    print("Done populating 10 rows via API.")

if __name__ == "__main__":
    populate_api()
