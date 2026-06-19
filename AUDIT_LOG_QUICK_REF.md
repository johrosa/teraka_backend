# Audit Log Page - Quick Reference

## 📍 URLs
- **Main Page**: `http://localhost:8000/admin/audit/`
- **Hash Verify API**: `http://localhost:8000/api/audit/verify/`

## 🔐 Access Requirements
✅ Must be logged in
✅ Must be staff member (is_staff=True)
✅ Django Admin redirect: Admin home → Audit Log

## 🎯 Quick Actions

### View All Recent Changes
```
1. Open /admin/audit/
2. Done! (page auto-loads latest 50 entries, newest first)
```

### Find Changes by Person
```
1. Open /admin/audit/
2. Select 👤 User dropdown
3. Click [🔍 Filtrer]
```

### Find Changes to Table
```
1. Open /admin/audit/
2. Select 📊 Table dropdown
3. Click [🔍 Filtrer]
```

### See Details of Change
```
1. Find entry in table
2. Click [📋 Afficher] button in Data column
3. Scroll to see full JSON data
4. Click [📋 Masquer] to hide
```

### Verify Data Hasn't Been Tampered
```
1. Open /admin/audit/
2. Click [✓ Vérifier l'intégrité (SHA256)]
3. Wait for verification
4. Read result:
   - ✓ = Chain intact, no tampering
   - ⚠️ = Anomalies detected!
```

## 📊 Filter Options

| Filter | Use For |
|--------|---------|
| 🔍 Search | Find by table name or user email (substring) |
| 📊 Table | Show only changes to specific table |
| ⚙️ Operation | Show only INSERTs, UPDATEs, or DELETEs |
| 👤 User | Show only changes by specific user |
| 📅 Date Range | Show changes between two dates |

**Tip**: Combine multiple filters!

## 🎨 Color Meaning

```
🟢 INSERT  = New record created
🟠 UPDATE  = Record modified
🔴 DELETE  = Record deleted
```

## 📋 What's in Each Row

| Column | Shows |
|--------|-------|
| ID | Unique audit entry number |
| Date/Time | When change occurred |
| Table | Which database table |
| Operation | INSERT, UPDATE, or DELETE |
| User | Who made the change (email or "system") |
| Hash | SHA256 tamper-evidence identifier |
| Data | Full change details (click to expand) |

## 🔐 Hash Chain Verification

**What it does**:
- Recomputes SHA256 hash for every audit entry
- Compares with stored hash
- If they match → Data is original ✓
- If they differ → Data was modified ⚠️

**How to use**:
1. Click [✓ Vérifier l'intégrité (SHA256)]
2. Wait for calculation (may take several seconds)
3. Result shows at top:
   - Green: "✓ Chaîne intacte" = All good
   - Red: "⚠️ Anomalies détectées" = Tampering found

## 📄 Example Filters

**Show all INSERT operations**
```
⚙️ Operation: [INSERT] → [🔍 Filtrer]
```

**Show December changes by John**
```
👤 User: [john@example.com]
📅 Date From: [2024-12-01]
📅 Date To: [2024-12-31]
→ [🔍 Filtrer]
```

**Show all changes to communes table**
```
📊 Table: [communes] → [🔍 Filtrer]
```

**Search for anything with "bosquet"**
```
🔍 Search: [bosquet] → [🔍 Filtrer]
```

## 🚀 Performance Tips

- **Page loads 50 entries** — scroll down for more
- **Hash verification can be slow** for large audit logs (1000+ entries)
- **Filter first** before running verification for better performance
- **Date range filter** helps narrow results if searching old data

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No entries showing | Check migration 0007 was applied |
| Can't access page | Verify you're staff member (is_staff=True) |
| Hash verification very slow | Audit log may be large; try filtering by table first |
| See "anonymous" user | Change was made directly in DB (via SQL), not through Django |
| Data looks corrupted | Click [📋 Afficher] to see full JSON; may just be truncated |

## 📱 Mobile Access

✅ Page is **fully responsive**
- Works on phones, tablets, and desktop
- Filters stack vertically on mobile
- Table scrolls horizontally if needed

## 🔗 Related Pages

- **Admin Home**: `/admin/`
- **RBAC Status**: `/admin/rbac/status/` (see user permissions)
- **User List**: `/admin/core/users/` (manage users)
- **Role Management**: `/admin/core/userrole/` (assign roles)

## 📚 Documentation

Full guides in project root:
- `AUDIT_LOG_PAGE.md` — Visual guide & detailed usage
- `RBAC_ADMIN_GUIDE.md` — RBAC system overview
- `README.md` — Migration commands section

## 🎓 What Audit Log Shows

✅ **Captured**:
- All INSERT, UPDATE, DELETE operations
- Who made the change (actor)
- When it happened (timestamp)
- What was changed (full row data)
- Database transaction ID

❌ **Not Captured**:
- SELECT queries (read-only)
- Django admin interface actions (unless they modify DB)
- HTTP requests (use separate logging for that)

## 🔐 Security Features

✅ Audit log is **append-only** (can't delete entries)
✅ Hash chain prevents **modification** (tampering detected)
✅ Staff-only access (protected with `@staff_member_required`)
✅ Login required (protected with `@login_required`)
✅ CSRF protection (standard Django)

## 💡 Pro Tips

1. **Regular verification**: Click hash verify weekly to ensure integrity
2. **Monitor deletes**: Filter by DELETE operation to see who's deleting
3. **User tracking**: Track specific user's changes over time
4. **Audit exports**: Can export table as CSV for reports (future feature)
5. **Narrow searches**: Use date range for faster queries on large datasets

## 🆘 Need Help?

1. Check `AUDIT_LOG_PAGE.md` for detailed visual guide
2. Check `RBAC_ADMIN_GUIDE.md` for RBAC-related audit questions
3. Run `python manage.py test_audit_log` to test system
4. Check Django logs: `/var/log/django/` (or check console output)
