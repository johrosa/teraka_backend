# Deployment Checklist: Django Groups ↔ PostgreSQL Roles Sync

## Overview
This step ensures Django auth.Group and PostgreSQL Role models stay synchronized across environments.

## Deployment Steps

### 1. **Pull Latest Code**
```bash
git pull origin main
```

### 2. **Install Dependencies** (if any)
```bash
pip install -r requirements.txt
```

### 3. **Run Migrations** (if needed)
```bash
python manage.py migrate
```
Note: No new migrations for this feature (signals don't require schema changes).

### 4. **Sync Existing Groups/Roles**
Run this command on first deployment to ensure all Groups and Roles are synchronized:

```bash
python manage.py sync_groups_roles --create
```

This will:
- Create missing Django Groups for all PostgreSQL Roles
- Create missing Roles for all Django Groups
- Show summary of sync status

### 5. **Verify Sync Status**
```bash
python manage.py sync_groups_roles
```

Output should show:
```
✅ SYNC COMPLETE: X Groups ↔ X Roles
```

### 6. **Test in Admin**
1. Go to Django Admin → Authentication → Groups
2. Create a new test group: "TEST_GROUP"
3. Check in DB: `SELECT * FROM core_role WHERE code='TEST_GROUP'`
4. Should exist automatically (signal executed)

---

## What Gets Deployed

### Files Modified
- `core/apps.py` — signals registered in ready()
- `core/signals.py` — NEW (sync handlers)
- `core/management/commands/sync_groups_roles.py` — NEW (sync command)

### What These Do
- **Signals** (core/signals.py): Auto-sync on create/update
- **Command** (sync_groups_roles.py): Manual check and bulk sync
- **AppConfig** (apps.py): Registers signals at startup

### Database Changes
**None** — Uses existing Role and Group models, no migrations needed.

---

## Deployment Environments

### Local Development
```bash
python manage.py sync_groups_roles --create
python manage.py runserver
```

### Staging
```bash
# On staging server
python manage.py migrate
python manage.py sync_groups_roles --create
systemctl restart gunicorn  # or your wsgi server
```

### Production
```bash
# On production server (via SSH or CI/CD)
python manage.py migrate
python manage.py sync_groups_roles --create --dry-run  # Preview first
python manage.py sync_groups_roles --create            # Apply
systemctl restart gunicorn
```

---

## Troubleshooting

### Q: Command not found
**A:** Ensure management command is in correct path:
```
core/management/commands/sync_groups_roles.py
```

### Q: Signals not triggering
**A:** Check that `core/apps.py` has `ready()` method:
```python
def ready(self):
    from core import signals  # noqa
```

### Q: Sync shows conflicts
**A:** Run with `--create` flag to auto-resolve:
```bash
python manage.py sync_groups_roles --create
```

### Q: Reverse sync needed?
**A:** To sync Roles → Groups only (not Groups → Roles):
Edit `core/signals.py` and disable the `sync_role_to_group_on_save` receiver.

---

## After Deployment

### Ongoing Maintenance
- **New groups created in admin?** → Role automatically synced (signal)
- **New roles from RBAC import?** → Group automatically synced (signal)
- **Need to verify status?** → Run `sync_groups_roles` anytime

### Rollback
If needed to revert this feature:
1. Remove signal registration from `core/apps.py`
2. Groups and Roles won't sync, but data remains intact
3. No rollback migration needed (no schema changes)

---

## Sync RBAC permissions to Django permissions

After synchronizing Groups and Roles, synchronize RBAC table/column grants to Django model permissions (auth.Permission).

Run these commands (preview first):

```bash
# Ensure Groups exist from roles
python manage.py sync_groups_roles --create
# Preview permission sync
python manage.py sync_rbac_permissions --dry-run
# Then apply permission sync
python manage.py sync_rbac_permissions --create
```

Notes:
- Run this after `sync_groups_roles` so Groups exist.
- Review `core/management/commands/sync_rbac_permissions.py` and adjust the `role_permission_map` to match your RBAC policy before applying in production.
- In CI/CD include the `sync_rbac_permissions` step after `sync_groups_roles`.

## CI/CD Integration

### GitHub Actions / GitLab CI Example
```yaml
deploy:
  stage: deploy
  script:
    - python manage.py migrate
    - python manage.py sync_groups_roles --create
    - systemctl restart gunicorn
  only:
    - main
```

### Docker Deployment
Add to your `docker-entrypoint.sh`:
```bash
#!/bin/bash
python manage.py migrate
python manage.py sync_groups_roles --create
exec gunicorn config.wsgi:application
```

---

## Summary for Deployments
1. ✅ Code is already committed (signals + command)
2. ✅ No migrations needed
3. ✅ Run `sync_groups_roles --create` on first deploy
4. ✅ Signals handle ongoing syncs automatically
5. ✅ Safe to deploy anytime (non-breaking)
