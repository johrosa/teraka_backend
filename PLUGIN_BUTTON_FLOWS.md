# Flux Détaillé des Boutons du Plugin Teraka QGIS

Ce document détaille chaque bouton du dockwidget, trace le flux d'exécution complet, et liste les fichiers/variables créées ou modifiées.

---

## 1. Bouton **"📂 Charger Projet"** (`loadProjectButton`)

### Signal connecté
```python
self.loadProjectButton.clicked.connect(self.on_load_project_clicked)
```

### Flux d'exécution
1. **Récupération du projet sélectionné**
   - Lit `self.projectComboBox.currentData()` → retourne le chemin du fichier `.qgz` ou `.qgs`
   - Cherche le fichier sur le disque via `os.path.exists(project_file)`

2. **Chargement du projet QGIS**
   - Appel `QgsProject.instance().read(project_file)`
   - Charge le fichier dans le canvas QGIS

3. **Notification utilisateur**
   - Affiche message succès via `self.plugin.iface.messageBar().pushMessage()`
   - Affiche avertissement si erreur

4. **Analyse automatique (optionnel)**
   - Après succès, appel `self.plugin.analyze_and_process_project()`
   - Lance l'analyse intelligente des couches du projet

### Fichiers modifiés/créés
- **Fichier chargé** : `<projet>.qgs` ou `<projet>.qgz` depuis `~/Mergin Projects/`
- **Fichier QSettings** (non visible) : `~/.config/QGIS/QGIS3.ini` — mémorise le dernier projet ouvert

### Variables/Objets modifiés
- `QgsProject.instance()` — état du projet QGIS remplacé par le fichier chargé
- `self.plugin.iface.canvas()` — canvas redessine les couches du nouveau projet

---

## 2. Bouton **"💾 Sauvegarder Projet"** (`saveProjectButton`)

### Signal connecté
```python
self.saveProjectButton.clicked.connect(self.plugin.save_current_project_configuration)
```

### Flux d'exécution
1. **Récupération du projet courant**
   - Récupère `QgsProject.instance()`

2. **Sérialisation des configurations**
   - Appel méthode plugin `save_current_project_configuration()`
   - Parcourt les couches du projet (`QgsProject.mapLayers()`)
   - Extrait les propriétés layer (nom, source, type, filtres, styles)

3. **Sauvegarde fichier .qgs**
   - Appel `QgsProject.instance().write(file_path)`
   - Écrit le projet sur disque

4. **Optionnel : Sauvegarde config Teraka**
   - Génère/met à jour un fichier JSON interne : `<projet>_teraka_config.json`
   - Contient :
     ```json
     {
       "layers": {
         "communes": {"endpoint": "communes", "geom_field": "geom"},
         "bosquet_gps": {"endpoint": "bosquet_gps", "geom_field": "geom"}
       },
       "filters": {"bosquet_gps": "created_at > '2025-01-01'"},
       "style_rules": {}
     }
     ```

### Fichiers modifiés/créés
- **Projet QGIS** : `<nom_projet>.qgs` ou `<nom_projet>.qgz` — sauvegarde l'état du projet
- **Config Teraka (optionnel)** : `<nom_projet>_teraka_config.json` — mémorise les filtres et styles

### Variables/Objets modifiés
- `QgsProject.instance()` — propriété `isDirty()` repasse à `False`
- Couches du projet — leurs propriétés source/style sont persistées

---

## 3. Bouton **"⬇️ Charger depuis BD"** (`loadDbButton`)

### Signal connecté
```python
self.loadDbButton.clicked.connect(self.plugin.load_database_data)
```

### Flux d'exécution
1. **Récupération de la table sélectionnée**
   - Lit `self.endpointComboBox.currentText()` → nom de la table (ex: `"bosquet_gps"`)
   - Récupère le mapping via `self.plugin.load_layer_mappings()` → dict avec `endpoint`, `geom_field`, `pk_field`

2. **Connexion PostgREST**
   - URL PostgREST : `http://localhost:3000/<table_name>`
   - Envoie GET request pour récupérer les données

3. **Création couche QGIS**
   - Si la table est géométrique (contient `geom_field`) :
     - Crée une `QgsVectorLayer` du type approprié (Point, LineString, Polygon, etc.)
     - URI PostgREST : `"postgrest?srid=4326&key=<pk_field>&geom_column=<geom_field>&uri=http://localhost:3000/<table>"`
   - Si non-géométrique :
     - Crée une couche table simple (pas de géométrie)

4. **Ajout au projet QGIS**
   - Appel `QgsProject.instance().addMapLayer(layer)`
   - Couche devient visible dans la légende du projet

5. **Notification**
   - Message succès/erreur dans la messagerie QGIS

### Fichiers modifiés/créés
- **Aucun fichier créé** (données lues en mémoire)
- **Projet QGIS** : nouvelles couches ajoutées, marqué `isDirty()=True`

### Variables/Objets modifiés
- `QgsProject.instance().mapLayers()` — ajoute nouvelle couche
- `QgsVectorLayer` — objet créé en mémoire (source PostgREST)
- État PostgREST — compteur de connexions +1

---

## 4. Bouton **"🔄 Comparer avec BD"** (`compareButton`)

### Signal connecté
```python
self.compareButton.clicked.connect(self.plugin.compare_project_with_db)
```

### Flux d'exécution
1. **Récupération des couches du projet**
   - Parcourt `QgsProject.instance().mapLayers()`
   - Filtre les couches avec source PostgREST

2. **Pour chaque couche**
   - Récupère l'ID table + clé primaire
   - Récupère les features actuelles de la couche
   - Récupère les features depuis PostgREST

3. **Comparaison**
   - Parcourt chaque feature (local vs distante)
   - Cherche les **différences** :
     - Feature locale supprimée en BD
     - Feature distante ajoutée
     - Feature modifiée (changement attributs/géométrie)

4. **Génération rapport**
   - Crée un objet dict / DataFrame avec les différences
   - Résumé : "N features insérées, M modifiées, K supprimées"

5. **Affichage résultat**
   - Ouvre une fenêtre de dialogue avec le rapport
   - Optionnel : export en CSV/JSON

### Fichiers modifiés/créés
- **Rapport comparaison (optionnel)** : `<projet>_comparison_<timestamp>.json` ou `.csv`
  ```json
  {
    "table": "bosquet_gps",
    "summary": {"inserted": 5, "modified": 3, "deleted": 1},
    "details": [
      {"action": "inserted", "id": 123, "geometry": {...}},
      {"action": "modified", "id": 45, "old_values": {...}, "new_values": {...}}
    ]
  }
  ```

### Variables/Objets modifiés
- `comparison_result` (variable temporaire) — dict avec résumé des différences
- Aucune modification du projet local (read-only)

---

## 5. Bouton **"🔃 Rafraîchir depuis API"** (`refreshFromApiButton`)

### Signal connecté
```python
self.refreshFromApiButton.clicked.connect(self.plugin.refresh_data_via_api)
```

### Flux d'exécution
1. **Récupération des couches PostgREST du projet**
   - Filtre `QgsProject.mapLayers()` → garder celles avec source `postgrest://`

2. **Pour chaque couche**
   - Récupère le mapping (endpoint, geom_field, pk_field)
   - Récupère les features depuis PostgREST (`http://localhost:3000/<endpoint>`)

3. **Mise à jour des données**
   - **Remplacement** : supprime les features locales, insère les distantes
   - Ou **Merge** : fusionne les changements

4. **Rafraîchissement du canvas**
   - Appel `layer.dataProvider().forceReload()`
   - Canvas redessine les couches

5. **Notification**
   - "Données mises à jour : N features chargées"

### Fichiers modifiés/créés
- **Aucun fichier créé** (modifications en mémoire)

### Variables/Objets modifiés
- Couches du projet (features remplacées/fusionnées)
- `QgsProject.instance()` — marqué `isDirty()=True` si changements
- Cache PostgREST — counters de requêtes +N

---

## 6. Bouton **"Données tests"** (`loadSampleDataButton`) ⭐ NOUVEAU

### Signal connecté
```python
self.loadSampleDataButton.clicked.connect(self.plugin.load_sample_data)
```

### Flux d'exécution
1. **Importation de la fonction de synthèse**
   ```python
   from mrv_teraka import create_synthetic_project_data
   ```
   - Import depuis `__init__.py` du plugin
   - Fonction définit dans `synthetic_data_generator.py`

2. **Création des couches synthétiques**
   - Appel `create_synthetic_project_data()`
   - Retourne liste de couches synthétiques (en mémoire) :
     ```python
     [
       QgsVectorLayer('Point?crs=EPSG:4326&field=id:integer&field=name:string',
                      'communes', 'memory'),
       QgsVectorLayer('Polygon?crs=EPSG:4326&field=id:integer&field=bosquet_id:integer',
                      'bosquet_gps', 'memory'),
       QgsVectorLayer('Point?crs=EPSG:4326&field=id:integer&field=arbre_id:integer',
                      'arbre_gps', 'memory'),
       # ... autres tables synthétiques
     ]
     ```

3. **Remplissage des features synthétiques**
   - Pour chaque couche, `_create_memory_layer()` génère :
     - `communes` : 5 features Polygon (communes fictives Mahajanga, Mandoto, etc.)
     - `bosquet_gps` : 10 features Polygon (parcelles synthétiques avec geom aléatoires)
     - `arbre_gps` : 50 features Point (arbres synthétiques répartis dans les bosquets)
     - `bosquet_baseline`, `arbre_baseline`, `membre_suivi`, etc. : features lookup tables

4. **Attribution des propriétés PostgREST**
   - Chaque couche reçoit les propriétés (depuis le mapping normalisé) :
     ```python
     layer.setCustomProperty('postgrest:endpoint', 'bosquet_gps')
     layer.setCustomProperty('postgrest:geom_field', 'geom')
     layer.setCustomProperty('postgrest:pk_field', 'id')
     ```

5. **Ajout au projet QGIS**
   - `QgsProject.instance().addMapLayer(layer)` pour chaque couche
   - Couches synthétiques apparaissent dans la légende

6. **Notification**
   - Message succès : "Couches synthétiques chargées : [communes, bosquet_gps, ...]"

### Fichiers modifiés/créés
- **Aucun fichier créé** (données 100% en mémoire, `memory://` provider)
- **Projet QGIS** : marqué `isDirty()=True` (ajout couches)

### Variables/Objets modifiés
- `QgsProject.instance().mapLayers()` — 10-15 couches `QgsVectorLayer` ajoutées
- Chaque couche a `QgsFeature` objects avec géométries et attributs synthétiques

### Fichier source : `synthetic_data_generator.py`
```python
DEFAULT_ENDPOINTS = {
    'communes': {...},
    'bosquet_gps': {...},
    'arbre_gps': {...},
    # ... 100+ mapping entries
}

def _create_memory_layer(name, geom_type, crs='EPSG:4326', fields=None):
    """Crée une couche mémoire vide avec schéma défini."""
    # Retourne QgsVectorLayer avec provider 'memory'

def generate_dummy_test_layers():
    """Génère les features synthétiques pour chaque couche."""
    # Parcourt DEFAULT_ENDPOINTS
    # Crée des geometries aléatoires (Point, Polygon, LineString)
    # Assigne les attributs

def create_synthetic_project_data():
    """Point d'entrée principal — retourne liste de QgsVectorLayer."""
    # Appel generate_dummy_test_layers()
    # Retourne layers
```

---

## 7. Bouton **"⚙️ Analyser Projet"** (`processProjectButton`)

### Signal connecté
```python
self.processProjectButton.clicked.connect(self.plugin.analyze_and_process_project)
```

### Flux d'exécution
1. **Scan des couches du projet**
   - Parcourt `QgsProject.instance().mapLayers()`
   - Collecte métadonnées : nom, type géométrie, nombre features

2. **Analyse de conformité**
   - Vérifie que chaque couche a une source PostgREST valide
   - Vérifie la présence des champs requis (pk_field, geom_field)
   - Détecte les tables sans géométrie

3. **Détection des dépendances**
   - Parcourt les foreign keys
   - Cherche les couches dépendantes manquantes
   - Ex : si `arbre_gps.bosquet_id` → FK `bosquet_gps`, vérifie que `bosquet_gps` existe

4. **Génération rapport d'analyse**
   - Crée un dict/JSON résumé :
     ```json
     {
       "project_name": "Suivi Itasy 2026",
       "layers_count": 12,
       "spatial_layers": 5,
       "non_spatial_tables": 7,
       "dependencies": {
         "arbre_gps": ["bosquet_gps", "especes_arbres"],
         "bosquet_gps": ["communes", "topographies"]
       },
       "warnings": ["Table utilisateurs manquante", "...]
     }
     ```

5. **Affichage résultat**
   - Ouvre fenêtre de dialogue avec l'analyse
   - Affiche liste des avertissements/erreurs

### Fichiers modifiés/créés
- **Rapport analyse (optionnel)** : `<projet>_analysis_<timestamp>.json`

### Variables/Objets modifiés
- Aucune (read-only, pas de modification du projet)

---

## 8. Bouton **"🚀 Préparer Mission"** (`autoPrepareButton`)

### Signal connecté
```python
self.autoPrepareButton.clicked.connect(self.plugin.auto_deploy_mission)
```

### Flux d'exécution
1. **Récupération du projet courant**
   - `QgsProject.instance().fileName()` → chemin `.qgz`

2. **Préparation du fichier pour Mergin Maps**
   - Copie du projet vers `~/Mergin Projects/<projet_name>/`
   - Ajout du fichier `.qgz` à la structure Mergin

3. **Configuration des couches pour synchronisation**
   - Parcourt les couches du projet
   - Configure les propriétés de synchronisation Mergin (`tracking`, `delete rules`, etc.)

4. **Initialisation du suivi des changements**
   - Crée table locale `_sync_log` pour tracer les changements

5. **Upload vers Mergin Maps**
   - Appel API Mergin : `POST /projects/<id>/push`
   - Télécharge le projet vers le serveur Mergin

6. **Notification**
   - "Mission préparée et téléchargée sur Mergin Maps"

### Fichiers modifiés/créés
- **Projet Mergin** : `~/Mergin Projects/<projet>/<projet>.qgz`
- **Table de sync** : `_sync_log` (table SQLite locale)
- **Fichier de config Mergin** : `~/Mergin Projects/<projet>/.mergin`

### Variables/Objets modifiés
- État du projet — marqué synchronisé

---

## 9. Bouton **"📥 Importer Mission"** (`autoImportButton`)

### Signal connecté
```python
self.autoImportButton.clicked.connect(self.plugin.auto_import_mission)
```

### Flux d'exécution
1. **Pull depuis Mergin Maps**
   - Appel API Mergin : `GET /projects/<id>/pull`
   - Télécharge les changements depuis le serveur

2. **Détection des changements locaux**
   - Parcourt la table `_sync_log`
   - Identifie les features ajoutées/modifiées/supprimées sur le terrain

3. **Fusion avec la base centrale**
   - Pour chaque changement, envoie un POST/PATCH vers PostgREST
   - URL : `http://localhost:3000/<table>` (POST) ou `http://localhost:3000/<table>?id=eq.<pk>` (PATCH)

4. **Mise à jour du projet**
   - Rafraîchit les couches du projet avec les données mises à jour

5. **Notification**
   - "N changements importés et synchronisés avec le serveur"

### Fichiers modifiés/créés
- **Table `_sync_log`** — vidée après import succès

### Variables/Objets modifiés
- Couches du projet — features mises à jour
- Base de données PostgREST — nouvelles données insérées

---

## 10. Bouton **"✅ Valider Mission"** (`autoValidateButton`)

### Signal connecté
```python
self.autoValidateButton.clicked.connect(self.plugin.auto_validate_mission)
```

### Flux d'exécution
1. **Chargement des règles de validation**
   - Récupère depuis le backend Django API : `GET /api/validation_rules/`
   - Règles métier Teraka (ex: "arbre_gps.hauteur > 0", "bosquet_gps.superficie < 50ha", etc.)

2. **Exécution des validations**
   - Parcourt les couches du projet
   - Pour chaque feature, applique les règles de validation

3. **Génération rapport de validation**
   - Crée dict avec statut chaque feature :
     ```json
     {
       "bosquet_gps": {
         "total": 10,
         "valid": 8,
         "errors": [
           {"id": 3, "error": "géométrie invalide", "geometry": "self-intersecting"},
           {"id": 5, "error": "superficie > max_allowed", "value": 60}
         ]
       }
     }
     ```

4. **Marquage des features invalides**
   - Surligne les features avec erreurs dans le canvas
   - Crée une couche de masque/symbologie spéciale

5. **Notification**
   - Affiche dialogue avec rapport : "8/10 valides, 2 erreurs détectées"

### Fichiers modifiés/créés
- **Rapport validation** : `<projet>_validation_<timestamp>.json`

### Variables/Objets modifiés
- Style des couches — features invalides surlignées
- Sélection du canvas — features en erreur sélectionnées

---

## 11. Bouton **"🔒 Finaliser Mission"** (`autoSyncButton`)

### Signal connecté
```python
self.autoSyncButton.clicked.connect(self.plugin.auto_finalize_mission)
```

### Flux d'exécution
1. **Vérification pré-finalisation**
   - Contrôle que toutes les features sont valides
   - Affiche avertissement si erreurs de validation détectées

2. **Marquage du projet comme finalisé**
   - Ajoute propriété projet : `"mission_status": "finalized"`
   - Ajoute timestamp : `"finalized_at": "2026-06-01T16:20:00"`

3. **Push final vers Mergin Maps**
   - Appel `POST /projects/<id>/push` avec flag `finalized=true`

4. **Archive sur le serveur Teraka**
   - Envoie les données finalisées vers PostgREST
   - Appel endpoint archive : `POST /api/mission_archive/`
   - Reçoit `archive_id` du serveur

5. **Notification**
   - "Mission finalisée et archivée. ID archive: 12345"

### Fichiers modifiés/créés
- **Projet marqué finalisé** — propriété sauvegardée dans `.qgz`

### Variables/Objets modifiés
- État du projet — `isDirty()=True` (puis saved)

---

## 12. Bouton **"🔄 Synchroniser les Listes"** (`refreshMappingsButton`)

### Signal connecté
```python
self.refreshMappingsButton.clicked.connect(self.on_refresh_mappings_clicked)
```

### Flux d'exécution
1. **Désactivation du bouton**
   - `self.refreshMappingsButton.setEnabled(False)`
   - Affiche "⏳ Synchronisation..."

2. **Appel au backend API**
   - Appel `self.plugin.refresh_api_mappings()`
   - GET request vers `http://localhost:8000/api/layer_mappings/`
   - Reçoit JSON de tous les mappings table/endpoint disponibles

3. **Mise à jour du cache local**
   - Écrit le fichier `layer_table_mapping.json` :
     ```json
     {
       "mappings": {
         "communes": {"endpoint": "communes", "geom_field": "geom"},
         "bosquet_gps": {"endpoint": "bosquet_gps", "geom_field": "geom"},
         ...
       }
     }
     ```

4. **Reconstruction des ComboBox**
   - Appel `self.populate_table_lists()`
   - Vide `self.endpointComboBox`
   - Ajoute tous les noms de tables (clés du dict)

5. **Réactivation du bouton**
   - `self.refreshMappingsButton.setEnabled(True)`
   - Affiche "🔄 Synchroniser les Listes"
   - Affiche dialogue succès

### Fichiers modifiés/créés
- **Mapping cache** : `layer_table_mapping.json` — mise à jour avec mappings du serveur

### Variables/Objets modifiés
- `self.endpointComboBox` — répeuplée avec tous les endpoints disponibles

---

## 13. Bouton **"Déconnexion"** (`logoutButton`)

### Signal connecté
```python
self.logout_button.clicked.connect(self.on_logout_clicked)
```

### Flux d'exécution
1. **Émission du signal**
   - `self.logout_requested.emit()`

2. **Traitement par le plugin principal**
   - Plugin capture le signal
   - Appel méthode `plugin.on_logout()`

3. **Suppression du token d'authentification**
   - Supprime token JWT du fichier config / QSettings
   - QSettings key : `"Teraka/api_token"`

4. **Réinitialisation de l'UI**
   - Appel `self.set_unauthenticated()`
   - Change statut label : "● Déconnecté" (rouge)
   - Désactive tous les boutons de contrôle

5. **Affichage du login**
   - Plugin ouvre fenêtre de connexion `auth_dialog.py`

### Fichiers modifiés/créés
- **QSettings** : clé `"Teraka/api_token"` supprimée

### Variables/Objets modifiés
- `self.status_label.text()` → "● Déconnecté"
- Tous les boutons `setEnabled(False)`

---

## Summary Table

| Bouton | Fichiers modifiés | Variables créées | Flux principal |
|--------|-------------------|------------------|----------------|
| **Charger Projet** | `.qgs/.qgz` | QgsProject | Disque → QGIS |
| **Sauvegarder Projet** | `.qgs/.qgz` + `_teraka_config.json` | — | QGIS → Disque |
| **Charger BD** | — | QgsVectorLayer (memory) | PostgREST → QGIS |
| **Comparer BD** | `_comparison.json` (opt) | comparison_result dict | Local ↔ PostgREST |
| **Rafraîchir API** | — | — | PostgREST → QGIS |
| **Données Tests** ⭐ | — | 10-15 QgsVectorLayer (memory) | synthetic_data_generator → QGIS |
| **Analyser Projet** | `_analysis.json` (opt) | analysis_report dict | QGIS → Report |
| **Préparer Mission** | `.qgz` + `_sync_log` | — | QGIS → Mergin |
| **Importer Mission** | — | — | Mergin → QGIS → PostgREST |
| **Valider Mission** | `_validation.json` | validation_report dict | Rules → QGIS |
| **Finaliser Mission** | `.qgz` (finalized flag) | archive_id | QGIS → Mergin → Teraka |
| **Synchroniser Listes** | `layer_table_mapping.json` | endpointComboBox repopulated | API → Cache → UI |
| **Déconnexion** | QSettings (token deleted) | — | QGIS → Auth Dialog |

