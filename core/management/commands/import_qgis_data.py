import os
import difflib
import logging
import xml.etree.ElementTree as ET
import zipfile
from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.gis.gdal import DataSource
from django.db import connection, models, transaction
from django.contrib.gis.geos import GEOSGeometry

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='import_spatial_data.log',
    filemode='a'
)


class Command(BaseCommand):
    help = 'Migration automatisée depuis un projet QGIS (.qgs/.qgz) vers PostGIS avec Fuzzy Matching'

    def add_arguments(self, parser):
        parser.add_argument('qgis_project', type=str, help='Chemin vers le fichier projet QGIS (.qgs ou .qgz)')
        parser.add_argument('--clear', action='store_true', help='Vider les tables existantes avant import')

    def parse_qgis_project(self, project_path):
        """Extrait les chemins des sources de données depuis le fichier projet QGIS (.qgs ou .qgz)."""
        sources = {}
        try:
            content = None

            # Gestion du format compressé .qgz
            if project_path.lower().endswith('.qgz'):
                with zipfile.ZipFile(project_path, 'r') as z:
                    qgs_files = [f for f in z.namelist() if f.endswith('.qgs')]
                    if qgs_files:
                        content = z.read(qgs_files[0])
            else:
                # Format .qgs classique
                with open(project_path, 'rb') as f:
                    content = f.read()

            if not content:
                raise ValueError("Impossible de lire le contenu du projet.")

            root = ET.fromstring(content)

            # Parcours des couches du projet
            for layer in root.findall(".//maplayer"):
                layer_name_elem = layer.find("layername")
                datasource_elem = layer.find("datasource")

                if layer_name_elem is not None and datasource_elem is not None:
                    layer_name = layer_name_elem.text
                    datasource = datasource_elem.text

                    if datasource:
                        # Nettoyage du datasource (QGIS ajoute souvent des options après '|')
                        clean_source = datasource.split("|")[0]

                        # On ignore les sources qui sont déjà des connexions PostGIS
                        if not clean_source.startswith("dbname="):
                            sources[layer_name] = clean_source

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la lecture du projet QGIS : {e}"))

        return sources

    def is_gps_data_pair(self, model_name):
        """
        Détecte si un modèle fait partie d'une paire GPS/Data.
        Retourne (is_pair, pair_type, qgis_layer_hint, is_gps_table)
        """
        gps_data_pairs = {
            'pggps': ('pg', 'petit_groupe', True),
            'pginfos': ('pg', 'petit_groupe', False),
            'arbregps': ('arbre', 'arbre', True),
            'arbrebaseline': ('arbre', 'arbre', False),
            'arbresuivi': ('arbre', 'arbre', False),
            'bosquetgps': ('bosquet', 'bosquet', True),
            'bosquetbaseline': ('bosquet', 'bosquet', False),
            'bosquetsuivi': ('bosquet', 'bosquet', False),
        }

        info = gps_data_pairs.get(model_name)
        if info:
            return (True, info[0], info[1], info[2])
        return (False, None, None, None)

    def get_geometry_field(self, model):
        """Retourne le champ géométrique du modèle s'il existe."""
        for field in model._meta.fields:
            field_type = str(type(field))
            if any(geo in field_type for geo in ['Point', 'Polygon', 'LineString', 'Multi', 'Geometry']):
                return field
        return None

    def import_features_direct(self, model, layer, clear_table=False):
        """
        Importe les features directement via GDAL + Django ORM.
        Évite les problèmes de LayerMapping avec les BooleanFields.
        """
        table_name = model._meta.db_table

        # Vider la table si demandé
        if clear_table:
            with connection.cursor() as cursor:
                cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
                self.stdout.write(f"Table {table_name} vidée")

        # Récupérer les champs du modèle
        model_fields = {f.name: f for f in model._meta.fields if not f.primary_key}
        geom_field = self.get_geometry_field(model)

        # Récupérer les champs de la source GDAL
        source_fields = [str(f) for f in layer.fields]

        imported_count = 0
        error_count = 0

        # Parcourir chaque feature
        for feature in layer:
            try:
                with transaction.atomic():
                    # Créer un dictionnaire de données pour l'instance
                    instance_data = {}

                    # Mapper les champs
                    for field_name, field_obj in model_fields.items():
                        # Skip les champs système
                        if field_name in ['id', 'created_at', 'updated_at']:
                            continue

                        # Skip les BooleanFields (problématiques)
                        if isinstance(field_obj, models.BooleanField):
                            continue

                        # Géométrie
                        if geom_field and field_name == geom_field.name:
                            try:
                                geom_wkt = feature.geom.wkt
                                instance_data[field_name] = GEOSGeometry(geom_wkt)
                            except Exception:
                                continue
                            continue

                        # Fuzzy matching pour trouver le champ source correspondant
                        matches = difflib.get_close_matches(field_name, source_fields, n=1, cutoff=0.6)
                        if not matches:
                            continue

                        source_field_name = matches[0]

                        try:
                            value = feature.get(source_field_name)

                            # Si None ou vide, skip
                            if value is None or value == '':
                                continue

                            # Gestion des ForeignKey
                            if isinstance(field_obj, (models.ForeignKey, models.OneToOneField)):
                                # Récupérer le modèle et champ cible
                                related_model = field_obj.remote_field.model
                                if hasattr(field_obj.remote_field, 'field_name') and field_obj.remote_field.field_name:
                                    target_field = field_obj.remote_field.field_name
                                else:
                                    target_field = 'id'

                                # Rechercher l'objet lié
                                try:
                                    related_obj = related_model.objects.get(**{target_field: value})
                                    instance_data[field_name] = related_obj
                                except related_model.DoesNotExist:
                                    continue
                                except Exception:
                                    continue

                            # Gestion des UUIDField
                            elif isinstance(field_obj, models.UUIDField):
                                instance_data[field_name] = value

                            # Gestion des IntegerField
                            elif isinstance(field_obj, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField)):
                                try:
                                    instance_data[field_name] = int(value)
                                except (ValueError, TypeError):
                                    continue

                            # Gestion des FloatField
                            elif isinstance(field_obj, models.FloatField):
                                try:
                                    instance_data[field_name] = float(value)
                                except (ValueError, TypeError):
                                    continue

                            # Gestion des DateTimeField
                            elif isinstance(field_obj, models.DateTimeField):
                                instance_data[field_name] = value

                            # Gestion des TextField/CharField
                            elif isinstance(field_obj, (models.TextField, models.CharField)):
                                instance_data[field_name] = str(value)

                            # Autres types
                            else:
                                instance_data[field_name] = value

                        except Exception as e:
                            continue

                    # Créer l'instance
                    if instance_data:
                        model.objects.create(**instance_data)
                        imported_count += 1

            except Exception as e:
                error_count += 1
                logging.error(f"Erreur import feature dans {table_name}: {str(e)}")

        return imported_count, error_count

    def handle(self, *args, **options):
        project_path = options['qgis_project']
        clear_tables = options['clear']

        # Validation du chemin du projet
        if not os.path.exists(project_path):
            self.stdout.write(self.style.ERROR(f"Le fichier {project_path} n'existe pas."))
            return

        # Parse du projet QGIS
        self.stdout.write("Analyse du projet QGIS...")
        qgis_sources = self.parse_qgis_project(project_path)

        if not qgis_sources:
            self.stdout.write(self.style.ERROR("Aucune source de données valide trouvée dans le projet."))
            return

        # Récupération des modèles Django
        app_models = list(apps.get_app_config('core').get_models())

        # Tri des modèles selon les dépendances
        def get_model_priority(model):
            model_name = model._meta.model_name

            # Priorité 0 : Communes
            if model_name == 'communes':
                return (0, 0)

            # Priorité 1 : Tables de référence (lookups)
            lookup_tables = [
                'especesarbres', 'formations', 'invasifs', 'lutteinvasifs',
                'luttenuisibles', 'nuisibles', 'produitsarbres', 'solcouleurs',
                'soltypes', 'sourcinggraines', 'sourcingplants', 'topographies',
                'typedocfoncier', 'utilisationarbres', 'utilisationsolbosquets',
                'cobeneficearbres', 'bienfaitagroforesteries'
            ]
            if model_name in lookup_tables:
                return (1, 0)

            # Priorité 2 : Users
            if model_name == 'users':
                return (2, 0)

            # Priorité 3 : PgInfos puis PgGps
            if model_name == 'pginfos':
                return (3, 0)
            if model_name == 'pggps':
                return (3, 1)

            # Priorité 4 : Membre
            if model_name == 'membre':
                return (4, 0)
            if model_name == 'membreinscrit':
                return (4, 1)

            # Priorité 5 : BosquetBaseline/Suivi puis BosquetGps
            if model_name == 'bosquetbaseline':
                return (5, 0)
            if model_name == 'bosquetsuivi':
                return (5, 1)
            if model_name == 'bosquetgps':
                return (5, 2)

            # Priorité 6 : ArbreBaseline/Suivi puis ArbreGps
            if model_name == 'arbrebaseline':
                return (6, 0)
            if model_name == 'arbresuivi':
                return (6, 1)
            if model_name == 'arbregps':
                return (6, 2)

            # Priorité 7 : MembreSuivi
            if model_name == 'membresuivi':
                return (7, 0)

            # Priorité 8 : Tables événements et documents
            if 'evenement' in model_name or 'document' in model_name:
                return (8, 0)

            # Priorité 9 : Tables de liaison (Answer*, Photo*)
            if model_name.startswith('answer') or model_name.startswith('photo'):
                return (9, 0)

            # Priorité 10 : Tables de paiement
            if 'paiement' in model_name:
                return (10, 0)

            # Priorité 11 : Autres tables
            return (11, 0)

        app_models.sort(key=get_model_priority)

        layer_names = list(qgis_sources.keys())
        success_count = 0
        error_count = 0

        # Traitement de chaque modèle
        processed_pairs = {}  # Garde trace des paires GPS/Data déjà traitées

        for model in app_models:
            table_name = model._meta.db_table
            model_name = model._meta.model_name
            self.stdout.write(f"\n--- Traitement de la table : {table_name} ---")

            # Vérifier si c'est une paire GPS/Data
            is_pair, pair_type, qgis_layer_hint, is_gps = self.is_gps_data_pair(model_name)

            if is_pair:
                # Si c'est une table Data (pas GPS), vérifier que le GPS a été importé
                if not is_gps:
                    if pair_type not in processed_pairs:
                        self.stdout.write(self.style.WARNING(
                            f"Table GPS pour {pair_type} pas encore importée, skip {table_name}"
                        ))
                        continue
                    # Utiliser la même source QGIS que la table GPS
                    qgis_layer_name = processed_pairs[pair_type]
                else:
                    # C'est une table GPS, chercher la couche QGIS
                    matches = difflib.get_close_matches(qgis_layer_hint, layer_names, n=1, cutoff=0.5)
                    if not matches:
                        msg = f"Aucune couche QGIS trouvée pour {table_name} (cherché: {qgis_layer_hint})"
                        self.stdout.write(self.style.WARNING(msg))
                        logging.warning(msg)
                        continue
                    qgis_layer_name = matches[0]
                    # Enregistrer pour les tables Data associées
                    processed_pairs[pair_type] = qgis_layer_name
            else:
                # Table normale, fuzzy matching classique
                matches = difflib.get_close_matches(table_name, layer_names, n=1, cutoff=0.5)
                if not matches:
                    msg = f"Aucune couche QGIS trouvée pour la table {table_name}"
                    self.stdout.write(self.style.WARNING(msg))
                    logging.warning(msg)
                    continue
                qgis_layer_name = matches[0]

            file_path = qgis_sources[qgis_layer_name]

            # Résolution du chemin relatif
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.path.dirname(project_path), file_path)

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"Fichier source introuvable : {file_path}"))
                continue

            self.stdout.write(f"Source QGIS : {qgis_layer_name} -> {file_path}")

            try:
                # Lecture de la source de données GDAL
                ds = DataSource(file_path)
                layer = ds[0]

                # Importation directe via GDAL + ORM
                imported, errors = self.import_features_direct(model, layer, clear_tables)

                self.stdout.write(self.style.SUCCESS(
                    f"Importation réussie pour {table_name}: {imported} enregistrements, {errors} erreurs"
                ))
                logging.info(f"SUCCÈS: {table_name} - {imported} enregistrements importés depuis {qgis_layer_name}")
                success_count += 1

            except Exception as e:
                error_msg = f"ERREUR sur {table_name}: {str(e)}"
                self.stdout.write(self.style.ERROR(error_msg))
                logging.error(error_msg)
                error_count += 1

        # Résumé final
        self.stdout.write(self.style.SUCCESS(
            f"\nTerminé ! Succès: {success_count}, Échecs: {error_count}. Consultez import_spatial_data.log."
        ))
