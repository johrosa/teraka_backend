# 🌳 TERAKA Platform - Page d'Accueil Plateforme

## 📋 Vue d'Ensemble

La page d'accueil TERAKA a été **complètement redesignée** pour présenter cette plateforme comme un outil de gestion des données du programme TERAKA, distinct du site officiel du projet. Elle affiche:

- ✅ Statistiques globales en temps réel
- ✅ Mission, Vision et Approche TERAKA
- ✅ 6 Objectifs de Développement Durable (ODD) de l'ONU
- ✅ Impact du programme de reboisement
- ✅ Informations sur les agriculteurs et groupes producteurs
- ✅ Plateforme de gestion des données
- ✅ Navigation vers les zones principales

---

## ✨ Changements Clés (Version 2.0)

### 🎨 Branding Teraka Authentique
- **Couleurs**: Vert forêt (#1b5e20), Or (#ffc107), Bleu (#1976d2)
- **Logo**: 🌳 TERAKA au lieu de générique
- **Tonalité**: Alignée avec mission officielle de reboisement communautaire

### 📋 Contenu Réorganisé
1. **Hero**: "Plateforme de Gestion des Données TERAKA"
2. **Mission & Vision**: 3 cartes explicatives
3. **ODD**: 6 Objectifs de Développement Durable visés
4. **Statistiques**: Communes, Bosquets, Arbres, Membres, PG
5. **Impact**: 6 résultats clés du programme
6. **Plateforme**: Fonctionnalités techniques
7. **Ressources**: Accès admin, APIs, support
8. **Footer**: Contacts réels et liens réseaux sociaux

---

## 🎯 Sections Détaillées

### Mission & Vision
Présente les 3 piliers du programme:
- **Mission**: Permettre aux communautés rurales de bénéfices durables de leurs plantations
- **Vision**: Modèle intégrant gestion des forêts et développement économique local
- **Approche**: Expertise scientifique + connaissances locales

### Objectifs de Développement Durable (ODD)
TERAKA contribue à 6 ODD des Nations Unies:
- **ODD 3**: Bonne Santé et bien-être
- **ODD 5**: Égalité des genres
- **ODD 8**: Travail décent
- **ODD 12**: Consommation responsable
- **ODD 13**: Action pour le climat
- **ODD 15**: Vie terrestre

### Statistiques Globales
Affiche en temps réel:
- **Communes**: Nombre de communes couvertes
- **Bosquets**: Total, en suivi, % couverture
- **Arbres**: Total, en suivi, % couverture
- **Agriculteurs**: Total participants, actifs, % activité
- **Groupes Producteurs**: Total, groupes actifs

### Impact du Programme
6 résultats clés showcased:
1. **Reforestation** - Arbres plantés, écosystèmes restaurés
2. **Revenus Durables** - Sources de revenus pour agriculteurs
3. **Formation & Développement** - Compétences et leadership
4. **Atténuation Climatique** - Réduction émissions GES
5. **Développement Social** - Conditions de vie, cohésion
6. **Autonomisation** - Gestion durable ressources naturelles

---

## 🎨 Design & Styling

### Palette Couleurs Teraka

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
