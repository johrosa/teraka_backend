# 💡 Exemples d'Utilisation - Interface de Consultation des Logs

## Table des Matières
1. [Accès à l'Interface Web](#accès-à-linterface-web)
2. [Utilisation de l'API](#utilisation-de-lapi)
3. [Filtrage Avancé](#filtrage-avancé)
4. [Intégration Programmée](#intégration-programmée)
5. [Cas d'Usage Réels](#cas-dusage-réels)

---

## Accès à l'Interface Web

### Exemple 1: Première Visite

1. Ouvrir le navigateur
2. Aller à: `http://localhost:8000/admin/audit-logs/`
3. Vous êtes redirigé vers la page de connexion si non authentifié
4. Après connexion, vous voyez la liste complète des logs

### Exemple 2: Accès via l'Admin Django

```
1. Aller à: http://localhost:8000/admin/
2. Connectez-vous
3. Cherchez "Audit Log" dans le menu de gauche
4. Cliquez sur "Audit logs"
5. Vous voyez la liste avec search et filtres
```

---

## Utilisation de l'API

### Configuration de Base

**Base URL**: `http://localhost:8000/api/audit-logs/`

**Authentification requise**: Token JWT ou Session Admin

### Exemple 1: Récupérer Tous les Logs (30 jours)

```bash
# Avec cURL
curl "http://localhost:8000/api/audit-logs/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Avec Python requests
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.get(
    "http://localhost:8000/api/audit-logs/",
    headers=headers
)

logs = response.json()
print(f"Nombre de logs: {logs['count']}")
for log in logs['data']:
    print(f"- {log['table_name']}: {log['operation']}")
```

**Réponse**:
```json
{
  "count": 150,
  "days": 30,
  "limit": 100,
  "timestamp": "2026-05-19T14:30:00.000Z",
  "data": [
    {
      "id": 421,
      "table_name": "bosquet_baseline",
      "operation": "UPDATE",
      "record_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "operateur1",
      "action_time": "2026-05-19T14:25:00.000Z",
      "old_data": {"surface_boisee_ha": 2.5},
      "new_data": {"surface_boisee_ha": 3.0},
      "current_hash": "abc123def456"
    }
  ]
}
```

### Exemple 2: Filtrer par Table

```bash
# Tous les logs de la table "membre"
curl "http://localhost:8000/api/audit-logs/?table_name=membre" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Logs de "bosquet_baseline" des 7 derniers jours
curl "http://localhost:8000/api/audit-logs/?table_name=bosquet&days=7" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Exemple 3: Filtrer par Opération

```bash
# Toutes les suppressions
curl "http://localhost:8000/api/audit-logs/?operation=DELETE" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Tous les UPDATE des 14 derniers jours
curl "http://localhost:8000/api/audit-logs/?operation=UPDATE&days=14" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# INSERT seulement
curl "http://localhost:8000/api/audit-logs/?operation=INSERT" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Exemple 4: Filtrer par Utilisateur

```bash
# Toutes les actions d'un utilisateur
curl "http://localhost:8000/api/audit-logs/?user_id=operateur123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Actions d'un utilisateur sur les 3 derniers jours
curl "http://localhost:8000/api/audit-logs/?user_id=operateur123&days=3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Exemple 5: Combinaison de Filtres

```bash
# Modifications d'un utilisateur spécifique sur une table
curl "http://localhost:8000/api/audit-logs/?table_name=membre&user_id=operateur1&operation=UPDATE" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Supprimer les dernières modifications de la semaine
curl "http://localhost:8000/api/audit-logs/?operation=DELETE&days=7&limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Filtrage Avancé

### Dans l'Interface Web

#### Scénario 1: Trouver Toutes les Modifications d'un Bosquet

```
1. Aller à /admin/audit-logs/
2. Dans "Recherche globale": entrer l'UUID du bosquet
3. Cliquer "Rechercher"
4. Tous les logs concernant ce bosquet s'affichent
5. Cliquer sur un log pour voir les détails
```

#### Scénario 2: Auditer les Modifications d'un Utilisateur

```
1. Aller à /admin/audit-logs/
2. Dans "Utilisateur": entrer l'ID utilisateur
3. (Optionnel) Sélectionner une "Table" spécifique
4. (Optionnel) Sélectionner une "Opération" spécifique
5. Cliquer "Rechercher"
```

#### Scénario 3: Trouver Toutes les Suppressions du Mois

```
1. Aller à /admin/audit-logs/
2. Dans "Opération": sélectionner "DELETE"
3. Cliquer "Rechercher"
4. Parcourir les résultats
5. Consulter les détails pour voir ce qui a été supprimé
```

---

## Intégration Programmée

### Exemple 1: Script Python pour Exporter les Logs

```python
import requests
import json
from datetime import datetime

class AuditLogExporter:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def fetch_logs(self, **filters):
        """Récupère les logs avec les filtres spécifiés"""
        response = requests.get(
            self.api_url,
            headers=self.headers,
            params=filters
        )
        return response.json()
    
    def export_to_json(self, filename, **filters):
        """Exporte les logs en JSON"""
        logs = self.fetch_logs(**filters)
        with open(filename, 'w') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        print(f"Logs exportés dans {filename}")
    
    def export_to_csv(self, filename, **filters):
        """Exporte les logs en CSV"""
        import csv
        logs = self.fetch_logs(**filters)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['id', 'table_name', 'operation', 'record_id', 
                           'user_id', 'action_time']
            )
            writer.writeheader()
            
            for log in logs['data']:
                writer.writerow({
                    'id': log['id'],
                    'table_name': log['table_name'],
                    'operation': log['operation'],
                    'record_id': log['record_id'],
                    'user_id': log['user_id'],
                    'action_time': log['action_time']
                })
        print(f"Logs exportés dans {filename}")

# Utilisation
exporter = AuditLogExporter(
    api_url="http://localhost:8000/api/audit-logs/",
    token="votre_token_jwt"
)

# Exporter tous les logs des 7 derniers jours
exporter.export_to_csv("logs_7jours.csv", days=7)

# Exporter les suppressions
exporter.export_to_json("deletions.json", operation="DELETE", days=30)

# Exporter les actions d'un utilisateur
exporter.export_to_csv("user_actions.csv", user_id="operateur1")
```

### Exemple 2: Script de Monitoring

```python
import requests
import time
from datetime import datetime

class AuditMonitor:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
        self.last_id = 0
    
    def check_deletions(self):
        """Vérifier s'il y a des suppressions"""
        response = requests.get(
            self.api_url,
            headers=self.headers,
            params={"operation": "DELETE", "days": 1}
        )
        
        logs = response.json()['data']
        if logs:
            print(f"⚠️  ALERTE: {len(logs)} suppressions détectées!")
            for log in logs:
                print(f"  - {log['table_name']} ({log['record_id']})")
                print(f"    Utilisateur: {log['user_id']}")
                print(f"    Date: {log['action_time']}")
        return logs
    
    def check_suspicious_activity(self):
        """Vérifier les activités suspectes"""
        response = requests.get(
            self.api_url,
            headers=self.headers,
            params={"limit": 50, "days": 1}
        )
        
        logs = response.json()['data']
        
        # Compter les actions par utilisateur
        user_actions = {}
        for log in logs:
            user = log['user_id'] or 'SYSTEM'
            user_actions[user] = user_actions.get(user, 0) + 1
        
        # Alerte si beaucoup d'actions
        for user, count in user_actions.items():
            if count > 100:
                print(f"⚠️  ALERTE: {user} a effectué {count} actions!")
        
        return user_actions

# Utilisation - Surveillance continue
monitor = AuditMonitor(
    api_url="http://localhost:8000/api/audit-logs/",
    token="votre_token"
)

while True:
    print(f"\n[{datetime.now()}] Vérification...")
    monitor.check_deletions()
    monitor.check_suspicious_activity()
    time.sleep(300)  # Vérifier toutes les 5 minutes
```

### Exemple 3: Rapport d'Audit Automatique

```python
import requests
from datetime import datetime, timedelta

class AuditReporter:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def generate_daily_report(self, email_to=None):
        """Générer un rapport quotidien"""
        response = requests.get(
            self.api_url,
            headers=self.headers,
            params={"days": 1, "limit": 1000}
        )
        
        logs = response.json()['data']
        
        # Statistiques
        operations = {}
        tables = {}
        users = {}
        
        for log in logs:
            op = log['operation']
            operations[op] = operations.get(op, 0) + 1
            
            table = log['table_name']
            tables[table] = tables.get(table, 0) + 1
            
            user = log['user_id'] or 'SYSTEM'
            users[user] = users.get(user, 0) + 1
        
        # Générer le rapport
        report = f"""
========== RAPPORT D'AUDIT QUOTIDIEN ==========
Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

RÉSUMÉ GLOBAL:
- Total d'actions: {len(logs)}
- Tables affectées: {len(tables)}
- Utilisateurs actifs: {len(users)}

RÉPARTITION PAR OPÉRATION:
"""
        for op, count in sorted(operations.items()):
            report += f"  {op}: {count}\n"
        
        report += "\nREPARTITION PAR TABLE:\n"
        for table, count in sorted(tables.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {table}: {count}\n"
        
        report += "\nACTIVITÉ PAR UTILISATEUR:\n"
        for user, count in sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {user}: {count}\n"
        
        report += "\n" + "="*45
        
        return report
    
    def send_report(self, email_to):
        """Envoyer le rapport par email"""
        import smtplib
        from email.mime.text import MIMEText
        
        report = self.generate_daily_report()
        
        # Configuration email (à adapter)
        msg = MIMEText(report)
        msg['Subject'] = f"Rapport d'Audit - {datetime.now().strftime('%d/%m/%Y')}"
        msg['From'] = "audit@teraka.local"
        msg['To'] = email_to
        
        # Envoyer (configuration SMTP à adapter)
        # smtplib.SMTP('localhost').sendmail(...)
        
        print(report)

# Utilisation
reporter = AuditReporter(
    api_url="http://localhost:8000/api/audit-logs/",
    token="votre_token"
)

# Générer et afficher le rapport
report = reporter.generate_daily_report()
print(report)

# Envoyer par email (optionnel)
# reporter.send_report("admin@teraka.local")
```

---

## Cas d'Usages Réels

### Cas 1: Vérifier les Modifications d'un Bosquet

**Situation**: Un bosquet a une surface différente que prévue. Vous voulez voir l'historique.

```
Étapes:
1. Aller à /admin/audit-logs/
2. Recherche globale: UUID du bosquet
3. Cliquer "Rechercher"
4. Voir tous les UPDATE et INSERT concernant ce bosquet
5. Cliquer sur chaque log pour voir les changements exacts
6. Identifier qui a fait quoi et quand
```

### Cas 2: Audit Mensuel

**Situation**: Vous devez produire un rapport mensuel des modifications.

```python
# Utiliser l'API pour récupérer les données
import requests
from datetime import datetime

api_url = "http://localhost:8000/api/audit-logs/"
headers = {"Authorization": "Bearer TOKEN"}

# Logs des 30 derniers jours
response = requests.get(
    api_url,
    headers=headers,
    params={"days": 30, "limit": 1000}
)

logs = response.json()['data']

# Analyser et générer le rapport
print(f"Total logs: {len(logs)}")
print(f"Période: {datetime.now().strftime('%d/%m/%Y')}")
print(...)
```

### Cas 3: Détecter une Erreur de Saisie

**Situation**: Un utilisateur a volontairement ou involontairement supprimé un enregistrement important.

```
Étapes:
1. Aller à /admin/audit-logs/
2. Filtre Opération: "DELETE"
3. Filtre Utilisateur: l'ID de l'utilisateur suspect
4. Cliquer "Rechercher"
5. Voir ce qui a été supprimé (dans old_data)
6. Date et heure exactes dans action_time
7. Pouvoir récupérer les données supprimées
```

### Cas 4: Conformité et Traçabilité

**Situation**: Audit externe ou interne demandant la traçabilité complète.

```bash
# Exporter tous les logs pour la période
curl "http://localhost:8000/api/audit-logs/?days=365&limit=10000" \
  -H "Authorization: Bearer TOKEN" \
  > audit_logs_2025.json

# Analyser pour conformité
# - Qui a accès?
# - Qu'ont-ils modifié?
# - Quand?
# - Les modifications étaient-elles autorisées?
```

---

## Astuces et Bonnes Pratiques

### ✅ À FAIRE:
- Consulter régulièrement les logs
- Configurer des alertes sur les suppressions
- Archiver les logs mensuellement
- Vérifier les modifications suspectes
- Documenter les changements importants

### ❌ À ÉVITER:
- Supprimer les logs (sauf pour archivage régulier)
- Ignorer les alertes de suppression
- Ne pas vérifier les modifications d'accès
- Laisser des comptes avec trop de permissions
- Modifier manuellement les hash

---

## Support et Ressources

- **Documentation complète**: `AUDIT_LOGS_GUIDE.md`
- **Implémentation technique**: `AUDIT_LOGS_IMPLEMENTATION.md`
- **Code source**: `core/views.py`, `core/admin.py`
- **Templates**: `core/templates/admin/audit_logs*.html`

---

**Dernière mise à jour**: 19 mai 2026

