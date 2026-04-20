# 🏠 Home Page Documentation

## Vue d'ensemble

La page d'accueil de Teraka Platform est une page de destination moderne et responsive qui affiche:

- ✅ Statistiques globales de la plateforme en temps réel
- ✅ Informations sur les communes, bosquets, arbres, membres
- ✅ Couverture des données (% de suivi vs baseline)
- ✅ Navigation vers les zones principales
- ✅ Informations sur l'utilisateur connecté

---

## 🎯 Fonctionnalités

### 1. **Navigation Header**
- Logo Teraka avec lien retour home
- Liens vers les sections principales
- Affichage de l'état de connexion
- Accès au panel admin (si connecté comme admin)

### 2. **Hero Section**
- Présentation de la plateforme
- Slogan et description
- Boutons d'action principaux

### 3. **Statistiques Globales**
Affiche en temps réel:

```
🗺️ Communes
   Total: 15

🌳 Bosquets  
   Baseline: 245
   Suivi: 189
   Couverture: 77.1%

🌲 Arbres
   Baseline: 5890
   Suivi: 3421
   Couverture: 58.1%

👥 Membres
   Total: 1203
   Suivi: 987
   Couverture: 82.0%

🤝 Producteurs Groupés
   Total: 489
   Suivi: 312
   Couverture: 63.8%
```

### 4. **À propos de Teraka**
- Description générale
- Caractéristiques clés
- Fonctionnalités principales

### 5. **Fonctionnalités Principales**
6 cartes d'action:

1. **Gestion des Rôles (RBAC)**
   - 7 niveaux de permission
   - Lien vers la gestion

2. **Statistiques en Temps Réel**
   - APIs statistiques
   - Lien vers l'endpoint

3. **Données Géospatiales**
   - Suivi des parcelles
   - PostGIS intégré

4. **Export & Rapports**
   - Export JSON/CSV
   - Rapports détaillés

5. **Interface d'Administration**
   - Gestion complète
   - Lien vers l'admin

6. **Documentation Complète**
   - Guides et exemples
   - API documentation

---

## 📱 Responsive Design

La page s'adapte automatiquement:

- **Desktop**: 3 colonnes pour les cartes
- **Tablet**: 2 colonnes
- **Mobile**: 1 colonne (plein écran)

---

## 🔌 URL et Routes

### Route:
```
GET / -> home_page_view()
```

### URL accessible:
```
http://localhost:8000/
```

### Redirection automatique:
- Sans authentification: Affiche page publique
- Avec authentification user: Affiche liens spécifiques
- Avec authentification admin: Affiche tous les liens + panel admin

---

## 🎨 Design & Styling

### Couleurs principales:
- **Primaire**: #2ecc71 (Vert)
- **Secondaire**: #3498db (Bleu)
- **Dark**: #2c3e50
- **Danger**: #e74c3c (Rouge)

### Features CSS:
- ✅ Gradients modernes
- ✅ Cartes avec animations au survol
- ✅ Barres de progression animées
- ✅ Responsive design complet
- ✅ Accessibilité (WCAG compliant)

---

## 📊 Contenu Dynamique

La page charge les statistiques en temps réel depuis la base de données:

```python
# core/views.py - home_page_view()

context = {
    'communes_count': Communes.objects.count(),
    'bosquets_total': BosquetBaseline.objects.count(),
    'bosquets_suivi': BosquetSuivi.objects.count(),
    'bosquets_coverage': (suivi / total * 100),
    # ... etc
}
```

---

## 🔐 Permissions

La page affiche différentes options selon l'utilisateur:

### Utilisateur non connecté:
- Affiche statistiques publiques
- Lien "Se Connecter"
- Lien "En savoir plus"

### Utilisateur connecté (staff):
- Affiche lien "Mon Dashboard"
- Affiche lien "Accéder à l'Administration"
- Affiche lien "Déconnexion"

### Administrateur (superuser):
- Affiche "ADMIN" badge
- Tous les liens d'admin
- API endpoints visibles

---

## 🚀 Déploiement

### En développement:
```bash
python manage.py runserver
# Accédez à: http://localhost:8000/
```

### En production:
```bash
gunicorn config.wsgi:application
# L'URL statique doit être configurée dans settings.py
```

### Configuration requise:
```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        # ...
    }
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## 📝 Fichiers impliqués

### Créés:
- `core/templates/home.html` - Template HTML (500+ lignes)
- `HOME_PAGE.md` - Cette documentation

### Modifiés:
- `core/views.py` - Ajout de `home_page_view()`
- `config/urls.py` - Ajout de la route home

---

## 🎓 Exemples d'utilisation

### Accès direct:
```
http://localhost:8000/
```

### Via lien de navigation:
```html
<a href="/">Accueil</a>
```

### Depuis Django template:
```html
<a href="{% url 'home' %}">Accueil</a>
```

### Depuis JavaScript:
```javascript
window.location.href = '/';
```

---

## 🔧 Personnalisation

### Ajouter une nouvelle statistique:

1. **Dans la vue (core/views.py)**:
```python
'ma_statistique': MyModel.objects.count(),
```

2. **Dans le template (home.html)**:
```html
<div class="stat-card">
    <div class="stat-icon">📊</div>
    <div class="stat-value">{{ ma_statistique }}</div>
    <div class="stat-label">Ma Statistique</div>
</div>
```

### Ajouter une nouvelle section:

1. Dupliquer une section existante dans le template
2. Modifier le contenu HTML
3. Ajouter les styles CSS si nécessaire

---

## 📞 Support

### Erreurs courantes:

**Erreur: Template not found (home.html)**
→ Vérifier que le fichier est dans `core/templates/home.html`

**Erreur: Database connection**
→ Les statistiques vont afficher une erreur généralement

**Page vierge sans CSS**
→ Vérifier que les STATIC_URL sont configurés

---

## ✅ Checklist de validation

- [x] Vue créée (home_page_view)
- [x] Template HTML créé (home.html)
- [x] Route URL ajoutée
- [x] Statistiques chargées dynamiquement
- [x] Responsive design implémenté
- [x] Navigation fonctionnelle
- [x] Documentation complète
- [x] Permissions vérifiées
- [x] Production-ready

---

**Version:** 1.0  
**Date:** 2026-04-20  
**Status:** ✅ Production-ready
