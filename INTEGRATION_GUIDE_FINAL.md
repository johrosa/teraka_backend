# 🚀 Guide d'Intégration et Déploiement Teraka

Ce guide détaille les étapes nécessaires pour mettre à jour la plateforme, stabiliser la base de données et activer le nouveau système d'audit.

---

## 🛠️ Étape 1 : Mise à jour du code
Assurez-vous d'avoir récupéré les derniers fichiers du dépôt :
```bash
git pull origin feature/stabilization
```

---

## 🗄️ Étape 2 : Alignement de la Base de Données (SQL)

### 2.1 Restauration de la Base
Le fichier `bd_teraka.sql` est un dump au format personnalisé PostgreSQL 17 (version 1.16). Pour le restaurer, vous devez utiliser `pg_restore` d'un client PostgreSQL 17 ou supérieur.

```bash
createdb -U postgres teraka
pg_restore -U postgres -d teraka bd_teraka.sql
```

### 2.2 Alignement du Schéma Django
Si vous travaillez avec une base de données préexistante (table `users` déjà là), vous devez exécuter le script de déploiement. Ce script ajoute les colonnes nécessaires pour Django Auth (`is_staff`, `is_superuser`, etc.) et synchronise le graphe de migration.

**Commande à exécuter :**
```bash
psql -U postgres -d teraka -f deployment_fix.sql
```

### 2.3 Configuration de PostgREST
PostgREST nécessite un rôle `authenticator` pour agir en tant que proxy pour les autres rôles.

```sql
-- Création des rôles de base
CREATE ROLE authenticator WITH NOINHERIT LOGIN PASSWORD 'votre_mot_de_passe';
CREATE ROLE anon NOLOGIN;

-- Autorisation pour PostgREST de changer de rôle
GRANT anon TO authenticator;
GRANT "Expansion_L1" TO authenticator;
GRANT "Expansion_L2" TO authenticator;
GRANT "MRV_L1" TO authenticator;
GRANT "MRV_L2" TO authenticator;
GRANT "MRV_L3" TO authenticator;
GRANT "Admin_L1" TO authenticator;
GRANT "Admin_L2" TO authenticator;

-- Permissions de base sur le schéma public
GRANT USAGE ON SCHEMA public TO anon, "Expansion_L1", "Expansion_L2", "MRV_L1", "MRV_L2", "MRV_L3", "Admin_L1", "Admin_L2";
```

Assurez-vous que `api/postgrest.conf` pointe vers la bonne base de données et utilise le rôle `authenticator`.

---

## 🔑 Étape 3 : Configuration Django & Création du Super-Utilisateur

### 3.1 Configuration JWT
Le système utilise un modèle utilisateur personnalisé avec un UUID (`uuid_user`). Assurez-vous que `config/settings.py` contient la configuration suivante pour SimpleJWT :

```python
SIMPLE_JWT = {
    # ... autres paramètres ...
    'USER_ID_FIELD': 'uuid_user',
}
```

### 3.2 Création du Super-Utilisateur
Le système utilise maintenant la table `users` pour l'authentification. Utilisez la commande dédiée pour créer votre premier accès administrateur :

```bash
python manage.py create_teraka_admin --email admin@teraka.org --password mon_mot_de_passe --nom "Admin" --prenom "Teraka" --genre "Masculin" --tel "+261340000000" --role "Admin_L2" --is_active "True"
```

**Options disponibles :**
- `--email` : Email de connexion (obligatoire, défaut: admin@teraka.org)
- `--password` : Mot de passe (défaut: admin)
- `--nom` : Nom de famille
- `--prenom` : Prénom
- `--genre` : Genre (Masculin/Féminin). Par défaut "Inconnu" pour satisfaire la contrainte NOT NULL de la base.
- `--tel` : Numéro de téléphone
- `--role` : Code du rôle PostgreSQL à assigner (ex: Admin_L2, MRV_L3, Expansion_L2)
- `--is_active` : Statut du compte (True/False). Défaut: True.

---

## 🛡️ Étape 4 : Activation du Système d'Audit
Le système d'audit permet de capturer l'identité des utilisateurs Django effectuant des actions via l'API.

1. **Installer les fonctions d'audit :**
```bash
psql -U postgres -d teraka -f final_audit_solution.sql
```

2. **Appliquer l'audit à une table (Exemple : `membre`) :**
Exécutez ce SQL pour chaque table que vous souhaitez auditer :
```sql
CREATE TRIGGER audit_membre
AFTER INSERT OR UPDATE OR DELETE ON membre
FOR EACH ROW EXECUTE FUNCTION audit_trigger('uuid_membre');
```

---

## 📥 Étape 5 : Import de données QGIS (Optionnel)
Si vous rencontrez des problèmes de mapping lors de l'import (cas des projets Mergin), utilisez le mode interactif :

```bash
python manage.py import_qgis_data mon_projet.qgz --interactive
```
*Les correspondances choisies seront sauvegardées en base de données pour les futurs imports.*

---

## ✅ Étape 6 : Vérification Finale
Lancez les serveurs et vérifiez l'accès à l'administration :
```bash
python run_servers.py
```
Accédez à : `http://localhost:8000/admin/`

---

### 🚨 En cas de problème
- **Error: "column users.is_staff does not exist"** -> Revoir l'Étape 2.
- **Error: "NodeNotFoundError"** -> Le script `deployment_fix.sql` s'occupe de marquer les migrations comme effectuées.
- **Accès Local Network** -> L'IP `192.168.0.172` est déjà autorisée dans `ALLOWED_HOSTS`.
