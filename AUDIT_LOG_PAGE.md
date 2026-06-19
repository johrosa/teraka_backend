# Audit Log Page - Visual & Usage Guide

## Page URL
```
http://localhost:8000/admin/audit/
```

## Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🔐 Audit Log - Piste d'audit infalsifiable                    │
│  Historique complet des modifications avec chaîne de hash SHA256 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  FILTER PANEL                                                    │
│  ┌─────────────┬──────────────┬──────────────┬──────────────────┐│
│  │ 🔍 Search   │ 📊 Table     │ ⚙️ Operation│ 👤 User          ││
│  │ [________]  │ [dropdown]   │ [dropdown]  │ [dropdown]       ││
│  ├─────────────┼──────────────┼──────────────┼──────────────────┤│
│  │ 📅 Date From│ 📅 Date To   │              │                  ││
│  │ [YYYY-MM-DD]│ [YYYY-MM-DD] │              │                  ││
│  ├─────────────┴──────────────┴──────────────┴──────────────────┤│
│  │ [🔍 Filtrer] [🔄 Réinitialiser]                             ││
│  │ [✓ Vérifier l'intégrité (SHA256)]                           ││
│  │ <Verification result area - appears after verification>     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Results: 1,234 entrée(s) trouvée(s)                            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ ID  │ Date/Heure      │ Table │ Op. │ User     │ Hash    │ Data │
├─────┼─────────────────┼───────┼─────┼──────────┼─────────┼──────┤
│ 456 │ 2024-12-19 ...  │ ✓ abc │ INS │ user@... │ abc123... │ [📋] │
│ 455 │ 2024-12-19 ...  │ ✓ def │ UPD │ admin@.. │ def456... │ [📋] │
│ 454 │ 2024-12-19 ...  │ ✓ xyz │ DEL │ system   │ xyz789... │ [📋] │
│ ... │ ...             │ ...   │ ... │ ...      │ ...       │ ... │
└─────┴─────────────────┴───────┴─────┴──────────┴─────────┴──────┘

Page 1 of 25  [« Première] [‹ Précédente] [Suivante ›] [Dernière »]
```

## Color Coding

### Operations
```
┌──────────┬────────────────┬──────────────────────────┐
│ Operation│ Color          │ Meaning                  │
├──────────┼────────────────┼──────────────────────────┤
│ INSERT   │ 🟢 Green       │ New record created       │
│ UPDATE   │ 🟠 Orange      │ Record modified          │
│ DELETE   │ 🔴 Red         │ Record deleted           │
└──────────┴────────────────┴──────────────────────────┘
```

### Left Border Indicator
```
Audit Entry
├─ 🟢 Green border  = INSERT
├─ 🟠 Orange border = UPDATE
└─ 🔴 Red border    = DELETE
```

## Data Display

### Row Expansion
```
Audit Entry Row
└─ [📋 Afficher] button (click to expand)
   ├─ Shows JSONB data
   ├─ Pretty-printed
   ├─ Max height 300px with scroll
   └─ Button changes to [📋 Masquer] when expanded
```

### JSON Data Structure
```json
{
  "op": "UPDATE",
  "schema": "public",
  "table": "bosquet_suivi",
  "data": {
    "id": 123,
    "uuid_bosquet_suivi": "abc-def-123",
    "date_suivi": "2024-12-19",
    "remarque": "Updated in field..."
  },
  "txid": 12345,
  "actor": "operator@example.com"
}
```

## Filter Examples

### Example 1: Find Updates to a Specific Table
```
📊 Table: [bosquet_suivi]
⚙️ Operation: [UPDATE]
[🔍 Filtrer]
→ Results: All UPDATEs on bosquet_suivi
```

### Example 2: Find User Activity in Date Range
```
👤 User: [analyst@teraka.org]
📅 Date From: [2024-12-01]
📅 Date To: [2024-12-31]
[🔍 Filtrer]
→ Results: All changes by analyst in December
```

### Example 3: Quick Search
```
🔍 Search: [commune]
[🔍 Filtrer]
→ Results: Any table/user containing "commune"
```

## Hash Verification Flow

### Step 1: Click Verification Button
```
┌────────────────────────────────────────┐
│ [✓ Vérifier l'intégrité (SHA256)]     │
└────────────────────────────────────────┘
                   ↓ (Click)
```

### Step 2: Verification In Progress
```
┌────────────────────────────────────────┐
│ [⏳ Vérification en cours...]          │
└────────────────────────────────────────┘
           ↓ (Server computes hashes)
```

### Step 3a: Success Result
```
┌────────────────────────────────────────────────────────────┐
│ ✓ Chaîne intacte! 1,234 entrée(s) vérifiée(s),          │
│   aucun changement détecté.                              │
└────────────────────────────────────────────────────────────┘
   (Green background)
```

### Step 3b: Failure Result (Tampering Detected)
```
┌────────────────────────────────────────────────────────────┐
│ ⚠️ Anomalies détectées! 3 entrée(s) compromise(s) sur    │
│    1,234.                                                  │
└────────────────────────────────────────────────────────────┘
   (Red background)
```

## Pagination Navigation

```
Page 1 of 25

[« Première] [‹ Précédente] [Page 1 of 25] [Suivante ›] [Dernière »]
                                  ↑
                            Current page indicator
```

**Features**:
- Filters persist across page navigation
- Each page shows 50 entries
- Links show all query parameters

## Mobile Responsive Behavior

### Desktop (1200px+)
```
┌─ Full 4-column filter grid
├─ Full table with all columns
└─ Horizontal pagination
```

### Tablet (768-1200px)
```
┌─ 2-column filter grid
├─ Slightly condensed table
└─ Flexible pagination
```

### Mobile (<768px)
```
┌─ 1-column filter grid (stacked)
├─ Minimal table (scrollable)
├─ Data truncated with scroll
└─ Vertical pagination buttons
```

## Security Indicators

### Hash Chain Verification
```
Hash Chain: ████████████████████ Intact
           Entry 1 → Entry 2 → Entry 3 → ...
           
If any entry is modified:
           Entry 1 → Entry 2 ✗ Entry 3 ✗ ...
                    (mismatch)
```

### Access Control
```
✅ Login Required: Only logged-in users can access
✅ Staff Required: Only staff members (is_staff=True) can view
✅ Read-Only: Cannot modify audit log entries
✅ CSRF Protected: Standard Django form protection
```

## Status Icons Used

```
🔐  Lock/Security
🔍  Search/Filter
📊  Table/Data
⚙️   Operation/Settings
👤  User/Person
🕐  Time/Date
🔴  Delete/Critical
🟠  Update/Warning
🟢  Insert/Success
✓   Verified/OK
⚠️   Warning/Caution
⏳  Loading/Processing
📋  Data/Information
🔄  Reset/Refresh
📅  Calendar/Date
```

## Common Tasks

### Task 1: Audit Recent Changes
```
1. Navigate to /admin/audit/
2. Results load automatically (latest first)
3. Scroll down to see older entries
4. Click [📋 Afficher] to see details
```

### Task 2: Find Specific User's Activity
```
1. Filter by 👤 User: [name@example.com]
2. Optional: Add date range
3. Click [🔍 Filtrer]
4. Review results and expand data as needed
```

### Task 3: Investigate Deletes
```
1. Filter ⚙️ Operation: [DELETE]
2. Optional: Select 📅 Date From (recent)
3. Click [🔍 Filtrer]
4. Review who deleted what and when
```

### Task 4: Verify Data Integrity
```
1. Navigate to /admin/audit/
2. Click [✓ Vérifier l'intégrité (SHA256)]
3. Wait for verification to complete
4. Read result message (green = OK, red = tampered)
```

### Task 5: Monitor Specific Table
```
1. Filter 📊 Table: [bosquet_suivi]
2. Optional: Select ⚙️ Operation: [UPDATE]
3. Optional: Add 📅 date range
4. Click [🔍 Filtrer]
5. Review all changes to that table
```

## Performance Notes

| Action | Typical Time |
|--------|------------|
| Page Load | 50-200ms |
| Filter/Search | 100-300ms |
| Hash Verification | 500ms-2s |
| Expand Data | Instant |
| Toggle Tab | Instant |

## Troubleshooting

**Q: No audit entries showing?**
- A: Ensure migration 0007 was applied: `python manage.py migrate`
- Check that audit triggers are active: `SELECT tgname FROM pg_trigger WHERE tgname LIKE 'audit_%';`

**Q: Hash verification slow?**
- A: Normal for large audit logs (1000+ entries)
- Consider filtering by table first

**Q: Can't access page?**
- A: Ensure you're logged in and staff member (is_staff=True)
- Check browser console for JavaScript errors

**Q: Data shows as "anonymous"?**
- A: Indicates DB user made change outside Django (direct SQL)
- Middleware only works for web requests

## API Endpoint

For programmatic access:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/audit/verify/?table=bosquet_suivi"
```

Response:
```json
{
  "status": "success",
  "chain_intact": true,
  "entries_checked": 1234,
  "invalid_count": 0,
  "verification": [
    {"id": 1, "valid": true, "operation": "INSERT", "event_time": "2024-12-19T10:30:00"},
    {"id": 2, "valid": true, "operation": "UPDATE", "event_time": "2024-12-19T10:35:00"}
  ]
}
```
