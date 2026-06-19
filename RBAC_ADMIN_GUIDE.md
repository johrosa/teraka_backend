# RBAC Admin System Guide

## Overview

The Teraka backend implements a **Role-Based Access Control (RBAC)** system that bridges Django authentication with PostgreSQL role-based permissions. This system allows fine-grained control over database access at the table and column level.

## Architecture Components

### 1. Models (core/models_rbac.py)

#### Role Model
- **Purpose**: Stores PostgreSQL role definitions in Django
- **Fields**:
  - `code` — unique identifier (e.g., `ADMIN`, `MRV`, `EXPANSION_L1`)
  - `description` — human-readable description
  - `level` — permission hierarchy level (0-3)
  - `created_at`, `updated_at` — timestamps

#### UserRole Model
- **Purpose**: Associates a Django user (Users model) with a PostgreSQL role
- **Constraints**: One-to-one relationship (one user → one role)
- **Fields**:
  - `user` — FK to Users (OneToOneField with CASCADE)
  - `role` — FK to Role (ForeignKey with PROTECT to prevent orphaning)
  - `created_at`, `updated_at` — timestamps

#### FieldMapping Model
- **Purpose**: Maps Django model fields to QGIS source fields for data synchronization
- **Unique constraint**: `(model_name, field_name)` ensures no duplicate mappings
- **Fields**:
  - `model_name` — target Django model name
  - `field_name` — target field in Django
  - `source_field_name` — corresponding field in QGIS
  - `comment` — documentation
  - `enabled` — toggle for activation

### 2. Role Hierarchy

#### Built-in PostgreSQL Roles (BASE_POSTGRES_ROLES)
- `Expansion_L1` — Create-only access (level 1)
- `Expansion_L2` — Create + modify access (level 2)
- `MRV_L1` — Read-only (level 1)
- `MRV_L2` — Read + modify (level 2)
- `MRV_L3` — Read + modify + validate (level 3)
- `Admin_L1` — Admin read + modify (level 1)
- `Admin_L2` — Admin read + modify + delete (level 2)

#### User Role Aliases (USER_ENUM_POSTGRES_ROLES)
- `ADMIN` — full database access (maps to nothing, grants all)
- `MRV` — field staff (maps to `MRV_L3`)
- `EXPANSION` — field operator (maps to `Expansion_L2`)
- `OP_SAISIE` — data entry (maps to `Expansion_L1`)
- `FINANCE` — finance team (maps to `Admin_L1`)
- `QUANTIFICATEUR` — quantifier (maps to `MRV_L2`)

Mapping defined in `USER_ROLE_PERMISSION_ALIASES`:
```python
{
    'MRV': 'MRV_L3',
    'EXPANSION': 'Expansion_L2',
    'OP_SAISIE': 'Expansion_L1',
    'FINANCE': 'Admin_L1',
    'QUANTIFICATEUR': 'MRV_L2',
}
```

### 3. Admin Views

#### UsersAdmin (core/admin.py line 65)
Displays and manages users with RBAC context:
- **List Display**: email, nom, prenom, role, operateur_id, c_com, is_active, is_staff, is_superuser
- **Fieldsets**:
  - Identite — personal info
  - Affectation — operateur_id, commune, role
  - Permissions — is_active, is_staff, is_superuser
  - Dates — date_joined, last_login

#### UserRoleAdmin (core/admin.py line 366)
Manages user-to-PostgreSQL role associations:
- **List Display**: user, role, get_role_description, created_at, updated_at, is_active_user
- **Key Methods**:
  - `save_model()` — validates one-to-one constraint, prevents duplicate role assignments
  - `is_active_user()` — shows boolean indicator of user active status
  - `get_role_description()` — displays role description
- **Permissions**:
  - Delete only allowed for superusers
  - OneToOne constraint enforced at save time

#### FieldMappingAdmin (core/admin.py line 112)
Manages QGIS-to-Django field mappings:
- **List Display**: model_name, field_name, source_field_name, enabled, updated_at
- **Search**: by model_name, field_name, source_field_name, comment
- **Ordering**: by model_name, then field_name

### 4. RBAC Import View (RBACImportView)

**Purpose**: Bulk import and apply RBAC permissions from CSV/Excel matrix

**Workflow**:
1. User uploads RBAC matrix file (CSV or Excel)
2. System auto-detects encoding and separator
3. Parses matrix with 8 skiprows (header rows)
4. **Role Creation**: Creates PostgreSQL roles if missing
5. **Permission Grant**: Applies permissions matrix (CRUD + validation)
6. **Role Inheritance**: Sets up aliases (e.g., MRV → MRV_L3)

**Permission Codes** (from CSV matrix):
- `C` — INSERT (Create) + USAGE on sequences
- `R` — SELECT (Read)
- `U` — UPDATE (Modify)
- `D` — DELETE (Destroy)
- `V` — UPDATE on status_validation column only

**Example Matrix Row**:
```
Table | Expansion_L1 | MRV_L3 | Admin_L2
------|--------------|--------|----------
bosquet_suivi | C | CRU | CRUD
```

**Error Handling**:
- Tries multiple encodings: UTF-8-sig, UTF-8, Latin-1, CP1252, ISO-8859-1
- Tries multiple separators: auto, semicolon, comma, tab
- Provides detailed error messages for failed imports
- Rolls back on error (database transaction safety)

### 5. RBAC Status View (RBACStatusView)

**Purpose**: Display current state of PostgreSQL roles and their table permissions

**Output**:
- Lists all expected roles
- For each role, shows:
  - List of tables with grants
  - Privilege types (SELECT, INSERT, UPDATE, DELETE, REFERENCES)

**Access**: Staff members only

## Integration Points

### Middleware Integration (core/middleware.py)

The audit middleware sets a session-level DB setting that RBAC can use:
```python
# In process_request:
set_config('app.audit_user', user_id, false)

# DB triggers read this for attribution
current_setting('app.audit_user', true)
```

### PostgREST Integration

- `db-anon-role` in `api/postgrest.conf` — anonymous/unauthenticated users (usually `web_anon`)
- JWT claims mapped to PostgreSQL roles
- PostgREST reads row-level security policies based on current role

### Audit Trail (core/migrations/0005_audit_log.py)

- DB triggers capture all DML (INSERT, UPDATE, DELETE) with actor attribution
- Trigger function reads `app.audit_user` setting (set by middleware)
- Falls back to `current_user` if middleware setting not available

## Admin Usage Workflow

### 1. Create a New Role (Admin)

1. Go to **Django Admin → Rôles PostgreSQL**
2. Click **Add Rôle**
3. Fill in:
   - Code: e.g., `MRV_L4`
   - Description: e.g., `MRV Level 4 - Custom permissions`
   - Level: e.g., `4`
4. Save

PostgreSQL role is created in next migration or via `Role.ensure_default_roles()`.

### 2. Assign Role to User (Admin)

1. Go to **Django Admin → Associations Utilisateur-Rôle**
2. Click **Add Association**
3. Select **User** and **Role**
4. Save
5. System confirms one-to-one constraint

To change a user's role:
- Edit existing UserRole record (don't create new)

### 3. Import RBAC Matrix (Admin)

1. Prepare RBAC matrix CSV/Excel with:
   - 8 header rows (skipped by import)
   - Row 9 onwards: Table name in column "Table", roles in other columns
   - Permission codes (C, R, U, D, V) in cells

2. Go to **Django Admin → RBAC Import** (if custom URL is configured)
   ```python
   # In core/urls.py (or admin site URLconf):
   path('admin/rbac-import/', RBACImportView.as_view(), name='rbac_import')
   ```

3. Upload file and submit
4. View status: **Django Admin → RBAC Status**

### 4. Verify RBAC State (Admin)

1. Go to **Django Admin → RBAC Status**
2. View roles and their table permissions
3. Verify expected grants are present

## Security Considerations

### 1. Function Ownership (audit_log_trigger)

- **Current**: Created with SECURITY DEFINER (execute as function owner)
- **Recommendation**: Verify owner is a restricted DB role
  ```sql
  SELECT proowner, proname FROM pg_proc WHERE proname = 'audit_log_trigger';
  ```

### 2. Audit Log Write Protection

- `REVOKE INSERT, UPDATE, DELETE ON public.audit_log FROM PUBLIC;`
- Only triggers can write to audit_log
- Regular users cannot modify audit records

### 3. Role Inheritance Risks

- `ADMIN` role grants ALL PRIVILEGES on all tables and sequences
- Use sparingly; prefer level-based roles (L1, L2, L3) for least privilege

### 4. User-Role Constraint

- OneToOne relationship prevents accidental multiple role assignments
- Enforced at save() time in UserRoleAdmin

## Database View (audit_log_view)

Migration `0007_audit_view` creates a readable view:

```sql
CREATE VIEW public.audit_log_view AS
SELECT
  a.id,
  a.event_time,
  a.schema_name,
  a.table_name,
  a.operation,
  a.row_data,
  a.changed_by,
  u.email AS changed_by_email,
  a.txid,
  a.prev_hash,
  a.row_hash
FROM public.audit_log a
LEFT JOIN public.users u ON u.uuid_user::text = a.changed_by;
```

**Benefits**:
- Joins audit_log with user emails for human readability
- Simplifies reporting and audit review

## Field Mapping Use Case

Used for **QGIS data synchronization**:
- QGIS maintains separate geometry and attribute tables
- Django models may have different field names
- FieldMapping resolves mismatches during import/sync

**Example**:
```
Model: BosquetBaseline
Field: uuid_bosquet_baseline
Source Field (QGIS): UUID_BOSQUET_BASELINE

Model: Communes
Field: c_com
Source Field (QGIS): CODE_COMMUNE
```

Load mappings:
```python
mappings = FieldMapping.load_mappings()
# {
#   ('bosquetbaseline', 'uuid_bosquet_baseline'): 'UUID_BOSQUET_BASELINE',
#   ('communes', 'c_com'): 'CODE_COMMUNE',
# }
```

## Testing & Validation

### Test Audit Log (core/management/commands/test_audit_log.py)

Validates audit trail and hash chain:

```bash
python manage.py test_audit_log
```

**Steps**:
1. Creates test_audit_table
2. Performs INSERT, UPDATE, DELETE
3. Displays audit_log rows
4. Recomputes hashes to verify chain integrity
5. Simulates tampering and shows detection

## Common Admin Operations

| Task | Path | Notes |
|------|------|-------|
| Create User | Users Admin | Email + nom required |
| Assign Role | UserRole Admin | One-to-one constraint enforced |
| Create Role | Role Admin | For custom roles beyond defaults |
| Map Fields | FieldMapping Admin | For QGIS sync |
| Import RBAC | RBACImportView (custom URL) | Bulk permission setup |
| View Permissions | RBACStatusView (custom URL) | Verify grants |
| Review Audit | audit_log_view (DB view) | Query with SQL or Django |

## Migration Commands

```bash
# Apply all pending migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reverse specific migration (use with caution)
python manage.py migrate core 0006

# Create new empty migration
python manage.py makemigrations core --empty --name my_change
```

## Troubleshooting

### Issue: UserRole assignment fails with "user already has a role"

**Solution**: Edit the existing UserRole instead of creating a new one.

### Issue: RBAC matrix import fails with encoding error

**Solution**: Ensure CSV/Excel file uses UTF-8 encoding. Try uploading as CSV instead of Excel.

### Issue: Role not appearing in PostgreSQL

**Solution**: Ensure migration 0004 has run. Verify with:
```sql
SELECT rolname FROM pg_roles WHERE rolname LIKE '%L%' OR rolname IN ('ADMIN', 'MRV', 'EXPANSION', 'OP_SAISIE', 'FINANCE', 'QUANTIFICATEUR');
```

### Issue: Audit log not capturing changes

**Solution**: Verify migration 0005 has run. Check trigger exists:
```sql
SELECT tgname FROM pg_trigger WHERE tgname LIKE 'audit_%';
```

## Related Documentation

- [RBAC_GUIDE.md](RBAC_GUIDE.md) — user-facing RBAC workflow
- [API_MANAGEMENT_VIEWS.md](API_MANAGEMENT_VIEWS.md) — admin monitoring endpoints
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) — configuration reference
