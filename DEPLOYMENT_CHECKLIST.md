## ✅ CHECKLIST DE DÉPLOIEMENT - RBAC AUTONOME

### 🎯 Objectif
Vérifier que toutes les URLs RBAC autonomes fonctionnent correctement après déploiement.

### 📋 Checklist avant déploiement

- [ ] Lire la documentation complète: `RBAC_GUIDE.md`
- [ ] Lire le résumé des changements: `RBAC_AUTONOME_SUMMARY.md`
- [ ] Vérifier que tous les fichiers sont présents (voir liste ci-dessous)
- [ ] Tester localement les URLs

### 📁 Fichiers modifiés/créés

**Fichiers MODIFIÉS:**
- [ ] `config/urls.py` - Ajout import et routes RBAC
- [ ] `core/views.py` - Ajout vue hub_rbac_view

**Fichiers CRÉÉS:**
- [ ] `core/templates/admin/rbac_hub.html` - Template du hub
- [ ] `RBAC_GUIDE.md` - Documentation utilisateur
- [ ] `RBAC_AUTONOME_SUMMARY.md` - Résumé des changements
- [ ] `test_rbac_urls.py` - Tests de vérification
- [ ] `DEPLOYMENT_CHECKLIST.md` - Ce fichier

### 🧪 Tests locaux à effectuer

#### 1️⃣ Vérifier les imports
```bash
cd backend_django
python -c "from core.views import rbac_hub_view; print('✅ Import OK')"
```
- [ ] Pas d'erreur ImportError

#### 2️⃣ Lancer le test d'URLs
```bash
python test_rbac_urls.py
```
- [ ] ✅ rbac_import URL enregistrée
- [ ] ✅ rbac_status URL enregistrée
- [ ] ✅ reverse() fonctionne

#### 3️⃣ Lancer le serveur Django
```bash
python manage.py runserver
```
- [ ] Serveur démarre sans erreur
- [ ] Pas d'erreur dans la console

#### 4️⃣ Tester les URLs dans le navigateur

| URL | Attendu | Résultat |
|-----|---------|----------|
| `http://localhost:8000/admin/rbac/` | Page hub RBAC | ☐ |
| `http://localhost:8000/admin/rbac/import/` | Formulaire d'import | ☐ |
| `http://localhost:8000/admin/rbac/status/` | Statut des permissions | ☐ |
| `http://localhost:8000/admin/core/userrole/` | Gestion des rôles | ☐ |

**Note:** Sans authentification, vous serez redirigé vers `/admin/login/`

#### 5️⃣ Tester l'authentification
```bash
# 1. Accéder à http://localhost:8000/admin/
# 2. Vous connecter avec un utilisateur administrateur
# 3. Retourner aux URLs RBAC
```
- [ ] Accès accepté après connexion admin
- [ ] Pages affichent correctement

#### 6️⃣ Vérifier le template du hub
- [ ] Les 4 cartes principales sont affichées
- [ ] Les boutons pointent vers les bonnes URLs
- [ ] La section "À propos" s'affiche correctement
- [ ] Le design responsive fonctionne (mobile/desktop)

#### 7️⃣ Tester les formulaires
- [ ] Upload d'un fichier sur `/admin/rbac/import/` fonctionne
- [ ] Les permissions s'affichent sur `/admin/rbac/status/`

### 📦 Étapes de déploiement

#### Sur le serveur de développement:
1. [ ] Pull les changements du repo Git
2. [ ] Vérifier que les fichiers sont bien présents
3. [ ] Lancer `python manage.py collectstatic` (si besoin)
4. [ ] Relancer le serveur Django
5. [ ] Effectuer les tests ci-dessus

#### Sur le serveur de production (BD préexistante):
1. [ ] Faire une sauvegarde complète de la base de données
2. [ ] Pull les changements du repo Git
3. [ ] Si les migrations échouent avec `NodeNotFoundError`, exécuter :
       `psql -U postgres -d teraka -f deployment_fix.sql`
4. [ ] Lancer `python manage.py migrate`
5. [ ] Lancer `python manage.py collectstatic`
6. [ ] Redémarrer le service Django/Gunicorn
7. [ ] Tester l'accès à l'Admin et aux Rôles
8. [ ] Vérifier les logs pour toute erreur de schéma

### 🔍 Vérifications post-déploiement

#### Accès aux URLs
- [ ] Utilisateur admin peut accéder `/admin/rbac/`
- [ ] Utilisateur admin peut accéder `/admin/rbac/import/`
- [ ] Utilisateur admin peut accéder `/admin/rbac/status/`
- [ ] Utilisateur non-admin est redirigé vers login

#### Fonctionnalités
- [ ] Import de matrice RBAC fonctionne
- [ ] Statut RBAC s'affiche correctement
- [ ] Gestion des rôles utilisateurs accessible
- [ ] Hub affiche les bonnes informations

#### Performances
- [ ] Pages chargent en < 2 secondes
- [ ] Pas de message d'erreur dans les logs
- [ ] Pas de fuites mémoire observées

#### Sécurité
- [ ] CSRF tokens présents sur les formulaires
- [ ] Authentification requise avant accès
- [ ] Permissions staff_member_required respectées

### 🚨 Résolution des problèmes

#### Erreur: "Page non trouvée 404"
**Solution:**
1. Vérifier que `core/urls.py` contient les routes
2. Vérifier que les imports sont corrects
3. Relancer le serveur Django

#### Erreur: "ImportError: cannot import name 'rbac_hub_view'"
**Solution:**
1. Vérifier que `rbac_hub_view` est défini dans `core/views.py`
2. Vérifier l'import dans `config/urls.py`
3. Vérifier la syntaxe Python

#### Erreur: "TemplateDoesNotExist: admin/rbac_hub.html"
**Solution:**
1. Vérifier que le fichier existe: `core/templates/admin/rbac_hub.html`
2. Vérifier la structure des répertoires
3. Lancer `python manage.py collectstatic`

#### Erreur: "Redirigé vers login même avec authentification"
**Solution:**
1. Vérifier que l'utilisateur est `is_staff=True`
2. Vérifier les permissions dans l'admin Django
3. Vérifier le middleware Django

### 📞 Support

En cas de problème après déploiement:

1. Consulter les logs:
   ```bash
   tail -f /var/log/django/app.log
   ```

2. Tester manuellement:
   ```bash
   python manage.py shell
   >>> from django.urls import reverse
   >>> reverse('rbac_hub')
   '/admin/rbac/'
   ```

3. Vérifier les permissions:
   ```bash
   psql -U postgres -d teraka
   \du  # Lister les rôles PostgreSQL
   ```

### ✨ Optimisations futures

- [ ] Cache le hub RBAC pour utilisateurs fréquents
- [ ] Ajouter historique des imports
- [ ] Notifications en cas de changement de permissions
- [ ] Export/Backup des matrices RBAC
- [ ] API REST pour automatisation

### 📝 Notes

- Garder cette checklist à jour
- Tester chaque déploiement systématiquement
- Documenter les problèmes rencontrés
- Mettre à jour la documentation si changements

---

**Dernier déploiement:** [DATE]
**Status:** ✅ À DÉPLOYER
**Validé par:** [SIGNATURE]