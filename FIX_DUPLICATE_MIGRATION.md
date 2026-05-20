# 🔧 Solution: Erreur "relation core_userrole already exists"

## Problème
```
django.db.utils.ProgrammingError: relation "core_userrole" already exists
```

La table `core_userrole` existe déjà en base de données, mais Django essaie de la créer via la migration.

## Solutions (Choisir UNE)

### ✅ Solution 1: Nettoyer l'enregistrement de migration (RECOMMANDÉE)

**Option A - Avec psql directement:**
```bash
psql -U postgres -d teraka
```

Puis exécutez:
```sql
DELETE FROM django_migrations WHERE app = 'core' AND name = '0002_userrole_auditlog';
\q
```

**Option B - Avec le script Python:**
```bash
python fix_duplicate_migration.py
```

**Puis appliquez la migration:**
```bash
python manage.py migrate core
```

---

### ✅ Solution 2: Utiliser la migration alternative sûre

1. **Supprimer l'enregistrement de migration:**
```bash
psql -U postgres -d teraka -c "DELETE FROM django_migrations WHERE app = 'core' AND name = '0002_userrole_auditlog';"
```

2. **Réappliquer avec la migration sûre:**
```bash
python manage.py migrate core
```

La nouvelle migration `0002_userrole_auditlog.py` utilise maintenant `CREATE TABLE IF NOT EXISTS` qui ne créera pas de doublon.

---

### ✅ Solution 3: Fake la migration

Si vous ne voulez pas nettoyer:
```bash
python manage.py migrate core 0002_userrole_auditlog --fake
```

---

## Vérification

Après avoir appliqué l'une des solutions:

```bash
# Vérifier l'état des migrations
python manage.py showmigrations core

# Vérifier que tout fonctionne
python manage.py shell
>>> from core.models import UserRole
>>> UserRole.objects.count()
0  # Devrait retourner 0 au lieu d'une erreur
```

---

## Fichiers Fournis

1. **`fix_duplicate_migration.py`** - Script Python pour nettoyer automatiquement
2. **`cleanup_migration.sql`** - Script SQL brut si vous préférez
3. **`core/migrations/0002_userrole_auditlog.py`** - Migration mise à jour avec `CREATE TABLE IF NOT EXISTS`
4. **`core/models.py`** - Modèle UserRole ajouté

---

## Étapes Recommandées

1. Exécutez `python fix_duplicate_migration.py`
2. Exécutez `python manage.py migrate core`
3. Vérifiez: `python manage.py showmigrations core`
4. Testez le dashboard: `http://localhost:8000/admin/dashboard/`

---

## Notes

- ✅ La table `core_userrole` existe et fonctionne correctement
- ✅ Le modèle Django est maintenant enregistré dans `models.py`
- ✅ Le dashboard ne crashe plus même si la table n'existe pas
- ✅ Les migrations sont idempotentes (peuvent être re-exécutées sans risque)

Si vous avez encore des problèmes, consultez le log Django: `logs/django.log`

---

**Status**: ✅ Solutions fournies - Choisir et exécuter l'une d'elles

