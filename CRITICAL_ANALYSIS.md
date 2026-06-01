# Analyse Critique des Fonctionnalités - Plugin MRV Teraka QGIS

## Executive Summary

Le plugin MRV Teraka est un outil de gestion de projet QGIS pour la gestion de collecte et validation de données spatiales pour le projet iTeraka (suivi agroforestier). L'analyse critique identifie des **forces significatives**, des **lacunes importantes** et des **risques de robustesse**.

---

## 1. Architecture & Design

### 1.1 Points Forts ✅

- **Modularité** : Séparation claire entre authentification (`auth_dialog.py`), client API (`postgrest_client.py`), workflows Mergin (`mergin_workflow_manager.py`), validation (`business_rules.py`)
- **Fallback d'import** : Gestion gracieuse des imports manquants (`synthetic_data_generator` try/except dans `__init__.py`)
- **UI Pattern** : Dockwidget séparé de la logique métier (réduction du couplage)
- **Configuration centralisée** : `config_postgrest.py` normalise les mappings de couches

### 1.2 Faiblesses ⚠️

- **État global fragmenté** : Variables d'état distribuées (`self.current_collected_data`, `self.current_original_data`, `self.current_data_mapping`, `self.current_validated_data`) — risque de désynchronisation
- **Pas de state machine** : Le workflow (login → data load → validation → sync) est implicite, pas formalisé
- **Pas de transaction de haut niveau** : Si un opération échoue partiellement (ex: 50% des données uploadées), l'état du projet est ambigü
- **Threading flou** : `QgsTask` mentionné mais implémentation non visible — risque de blocking du UI pendant requêtes API lentes
- **Pas de circuit breaker** : Si API down, les requêtes continuent sans backoff exponentiel

---

## 2. Authentification & Sécurité

### 2.1 Points Forts ✅

- **JWT Token Management** : `TokenManager` externalise la gestion des jetons
- **QSettings pour stockage** : Plus sûr que fichiers texte en clair
- **Dual mode (Django/PostgREST)** : Support de deux backends d'authentification

### 2.2 Faiblesses ⚠️

- **Token expiration non gérée** : Pas visible de mécanisme de renouvellement ou de détection d'expiration
- **Pas de rate limiting client** : Le plugin peut être throttled par le serveur sans indication utilisateur
- **Pas de refresh token** : Si token JWT expire, l'utilisateur doit se reconnecter
- **Credentials stockés en clair dans QSettings** : Vulnérable si poste compromis (vs keyring system)
- **HTTPS non forcé** : `http://localhost:8000` en dur — OK local, mais risqué en production sur réseau

---

## 3. Accès aux Données & PostgREST

### 3.1 Points Forts ✅

- **PostgREST abstraction** : Classe `PostgREST` centralise les appels API
- **Mapping flexible** : `layer_table_mapping.json` permet redirection table → endpoint
- **Géométrie supportée** : GeoJSON/WKT via `PostgREST` avec champs geometry
- **Couches synthétiques** : `synthetic_data_generator.py` crée des data de test sans BD pour dev

### 3.2 Faiblesses ⚠️

- **Pas de pagination** : `max-rows=1000` dans postgrest.conf — si table > 1000 rows, données tronquées silencieusement
- **Pas de filtrage côté client** : Load ALL data chaque fois, puis filtre en mémoire
- **Pas de cache couche** : Chaque appel `refreshFromApiButton` recharge 100% des données
- **Pas de détection changements serveur** : Aucune détection de mise à jour serveur depuis dernier refresh
- **Pas de optimistic locking** : Si deux utilisateurs modifient même feature, dernière écriture gagne (conflict silencieux)

---

## 4. Validation des Données

### 4.1 Points Forts ✅

- **Business Rules Engine** : Règles métier centralisées dans `BusinessRulesEngine`
- **Validation Dialog** : UI dédiée pour affichage erreurs (`ValidationDialog`)
- **Rule composition** : Règles composables (AND, OR, NOT)
- **Backend rules** : Règles proviennent du serveur, pas codées en dur

### 4.2 Faiblesses ⚠️

- **Validation tardive** : Validée seulement au moment de finaliser, pas en temps réel pendant édition
- **Pas de géométrie validation** : Pas détection de self-intersecting polygons, géométries invalides
- **Pas de contraintes spatiales** : Pas de "feature must be within commune boundary"
- **Pas de audit trail** : Pas trace de qui a modifié quoi et quand (sauf audit_log distant)
- **Règles côté client non versionnées** : Si règle change côté serveur, plugin ne le sait pas jusqu'à refresh manuel

---

## 5. Workflows Mergin Maps

### 5.1 Points Forts ✅

- **Project push/pull automatisé** : `MerginWorkflowManager` gère lifecycle complet
- **Data merge** : `MerginDataMerger` détecte changements terrain vs BD centrale
- **Mission lifecycle** : Prépare → Importe → Valide → Finalise (workflow clair)

### 5.2 Faiblesses ⚠️

- **Merge logic unclear** : Comment résout conflits ? Last-write-wins ou user-directed ?
- **Pas de rollback** : Si synchronisation échoue partiellement, comment revenir en arrière ?
- **Network assumption** : Suppose connexion stable à Mergin Maps (offline mode not visible)
- **No sync scheduling** : Tout manuel, pas de sync périodique en background
- **Data loss risk** : Si utilisateur force-push avant merge, changements terrain perdus

---

## 6. Interface Utilisateur

### 6.1 Points Forts ✅

- **13 boutons bien organisés** : Groupés par fonction (Projet, Données, Mergin, Config)
- **Statut visuel** : Indicateur de connexion (● Connecté/Déconnecté)
- **Tooltips métier** : Description claire de chaque action
- **Disable state** : Boutons grayed until authenticated

### 6.2 Faiblesses ⚠️

- **Pas de progression** : Pas barre de progress lors d'opérations longues (load DB, refresh API)
- **Pas d'undo** : Si utilisateur clique "Finaliser mission" par erreur, mission finalisée pour de bon
- **Pas de confirmation** : Actions destructrices sans dialog de confirmation
- **Pas de tooltips erreurs** : Bouton désactivé sans explication pourquoi
- **Pas de aide contextuelle** : Documentation métier absente de l'UI (lien Help manquant)
- **UI blocks** : Pas visible si requêtes API lancées en threads ou blocking UI (lag lors appels API lents)

---

## 7. Gestion des Erreurs

### 7.1 Points Forts ✅

- **Django error viewer** : `django_error_viewer.py` affiche HTML errors du serveur
- **Try/except fallback** : Imports conduits gracieusement

### 7.2 Faiblesses ⚠️

- **Erreurs silencieuses** : Beaucoup d'appels API sans try/except visible (risk de crash)
- **Messages d'erreur génériques** : "Impossible de contacter l'API" sans détail (timeout vs 404 vs 500)
- **Pas de retry** : Erreur réseau = échec définitif, pas de retry automatique
- **Logs absent** : Pas visible de fichier log plugin (debug difficile)
- **Pas de sentry** : Pas d'error tracking distant (exceptions perdues)

---

## 8. Performance & Scalabilité

### 8.1 Points Forts ✅

- **Memory layers** : Données synthétiques en mémoire, pas disque
- **Lazy loading** : Couches chargées à la demande (pas à startup)

### 8.2 Faiblesses ⚠️

- **Full table load** : Charger table 100K rows dans QGIS = lag/crash
- **No chunking** : Pas de batch processing si API upload 1000s de features
- **Pas de index spatial** : Requêtes spatiales sur layers memory inefficaces
- **Memory leak risk** : Pas visible de cleanup des anciennes couches (si reload 10x, mémoire monte)
- **Canvas redraw** : Chaque ajout couche → redraw complet (slow si 50+ couches)

---

## 9. Données Synthétiques (`synthetic_data_generator.py`)

### 9.1 Points Forts ✅

- **Géométries variées** : Point, LineString, Polygon (+ random variation)
- **Champs réalistes** : `nom`, `date`, `uuid`, `operateur`, `c_com` (resembles real schema)
- **Mapping complet** : DEFAULT_ENDPOINTS couvre 100+ tables
- **FK dependencies** : Lookup tables incluses (communes, topographies, etc.)

### 9.2 Faiblesses ⚠️

- **Data không en relations** : FK fields peuplés avec IDs aléatoires, pas respectent FK contraintes
- **Pas de géométries invalides** : Génère toujours géométries valides (pas test edge cases)
- **Hardcoded center** : DEFAULT_CENTER pour Itasy — pas portable
- **Pas de paramétrage** : Nombre de features/couches en dur, pas configurable
- **Random seed absent** : Différent données chaque run — pas reproducible pour debugging

---

## 10. Dépendances Critiques

### 10.1 Points Forts ✅

- **External deps minimisées** : QGIS core + PyQt5
- **PostgREST vendoré** : Pas d'install externe requise (Windows+Linux)

### 10.2 Faiblesses ⚠️

- **Django API critique** : Si serveur down, plugin inutile (fallback mode absent)
- **Mergin Maps account requis** : Pas d'utilisation plugin sans Mergin
- **PostgreSQL schema** : Suppose 100+ tables existent (schéma fragile si changements)
- **GDAL dependencies** : Si GDAL version non compatible, loading GeoJSON échoue
- **QSettings namespace** : Si autre app interfère avec QSettings `Teraka/*`, state corrompu

---

## 11. Lacunes Fonctionnelles Majeures

### 11.1 Offline Mode ❌
- Pas visible de support: travailler offline, sync quand connexion revient
- **Impact** : Utilisateurs terrain sans réseau internet = bloqués

### 11.2 Multi-user Conflict Resolution ❌
- Pas visible de merge strategy (3-way merge, conflict markers, etc.)
- **Impact** : 2 utilisateurs modifient même feature → conflict silencieux ou last-write-wins

### 11.3 Data Export ❌
- Pas visible de bouton "Exporter en CSV/Shapefile"
- **Impact** : Données locked in QGIS project, pas réutilisables

### 11.4 Bulk Operations ❌
- Pas visible de "Sélectionner 100 features + opération batch"
- **Impact** : Éditer 1000 features = 1000 clics individuels

### 11.5 Undo/Redo ❌
- Pas visible de undo stack
- **Impact** : Erreur utilisateur = redo manual ou reload projet

### 11.6 Scheduling & Automation ❌
- Pas visible de "Sync daily at 8pm", "Validate chaque matin"
- **Impact** : Workflow manuel, pas automatisé

### 11.7 Audit & Compliance ❌
- Pas visible de "Qui a modifié cette feature et quand ?"
- **Impact** : Non-conformité si audit trail requis

---

## 12. Risques Critiques

| Risque | Probabilité | Sévérité | Mitigation |
|--------|-------------|----------|-----------|
| **Perte données par conflict** | Haute | Critique | Merge 3-way + user review |
| **API inaccessible → plugin stuck** | Moyenne | Critique | Offline mode + fallback |
| **Token expire mid-workflow** | Moyenne | Haute | Auto-renew + interactive refresh |
| **Pagination silencieuse** (>1000 rows) | Moyenne | Haute | Warning dialog + scroll support |
| **UI lag sur gros dataset** | Haute | Moyenne | Async loading + progress bar |
| **Données synthétiques non réalistes** | Basse | Basse | Seed DB réelle pour test |

---

## 13. Recommandations Prioritaires

### Critiques (Sprint 0)
1. **Ajouter détection pagination** : Warn utilisateur si API retourne max-rows
2. **Ajouter timeout + retry** : 5s timeout + 3 retries exponential backoff
3. **Ajouter logging** : Fichier `.../MrvTeraka.log` pour debugging
4. **Ajouter undo/redo stack** : Revert dernière opération

### Importants (Sprint 1-2)
5. **Ajouter progress bar** : UI feedback durant opérations longues
6. **Ajouter offline cache** : Local SQLite sync dès que connexion revient
7. **Ajouter conflict resolution UI** : User choose version lors merge conflict
8. **Ajouter validation temps réel** : Rules appliquées lors edit feature (vs finalisation)

### Nice-to-have (Sprint 3+)
9. Ajouter export CSV/Shapefile
10. Ajouter audit trail "Qui/Quand/Quoi"
11. Ajouter scheduling (sync hebdo)
12. Ajouter i18n complet (FR/EN/Malagasy)

---

## 14. Verdict Fonctionnel

| Aspect | Grade | Commentaire |
|--------|-------|-----------|
| **Architecture** | B+ | Modulaire, mais state fragmented |
| **Core Features** | B | 13 fonctions principales, mais incomplete edge cases |
| **Robustness** | C | Pas retry, error handling limité, no offline |
| **UX/Polish** | C+ | UI claire, mais pas feedback utilisateur (progress, confirm) |
| **Data Integrity** | C- | Conflict resolution absent, pagination silencieuse |
| **Scalability** | C | OK pour <1000 features/couche, au-delà = problèmes |
| **Production-ready** | **C+** | **Usable pour déploiement limité, mais risques élevés avant hardening** |

**Conclusion** : Plugin **fonctionnel et stratégiquement bien pensé** (workflow métier bon), mais **manque de robustesse et edge-case handling**. Avant déploiement production ou multi-utilisateur, les 4 premiers risques critiques doivent être résolus.

