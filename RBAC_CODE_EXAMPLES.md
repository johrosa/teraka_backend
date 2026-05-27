## 💻 Exemples de Code - RBAC Autonome

### Exemples Python

#### 1. Obtenir les URLs RBAC

```python
from django.urls import reverse

# URL du hub central
hub_url = reverse('rbac_hub')
print(hub_url)  # Output: /admin/rbac/

# URL d'import
import_url = reverse('rbac_import')
print(import_url)  # Output: /admin/rbac/import/

# URL du statut
status_url = reverse('rbac_status')
print(status_url)  # Output: /admin/rbac/status/

# URL de gestion des rôles
roles_url = reverse('admin:core_userrole_changelist')
print(roles_url)  # Output: /admin/core/userrole/
```

#### 2. Construire des liens vers RBAC

```python
from django.urls import reverse
from django.contrib.admin import AdminSite

# Dans une vue
def my_view(request):
    context = {
        'rbac_hub': reverse('rbac_hub'),
        'rbac_import': reverse('rbac_import'),
        'rbac_status': reverse('rbac_status'),
    }
    return render(request, 'template.html', context)

# Dans un template
# {% url 'rbac_hub' %} → /admin/rbac/
# {% url 'rbac_import' %} → /admin/rbac/import/
# {% url 'rbac_status' %} → /admin/rbac/status/
```

#### 3. Vérifier les rôles de l'utilisateur

```python
from core.models import UserRole
from django.shortcuts import get_object_or_404

def get_user_role(user):
    """Obtenir le rôle PostgreSQL d'un utilisateur"""
    try:
        user_role = UserRole.objects.get(user=user)
        return user_role.role.role_name
    except UserRole.DoesNotExist:
        return None

def get_user_permissions(user):
    """Obtenir les permissions d'un utilisateur"""
    role = get_user_role(user)
    if role:
        # Ici, faire une requête pour obtenir les permissions
        # depuis la matrice RBAC
        return role.get_permissions()
    return []

# Utilisation
role = get_user_role(request.user)
if role:
    print(f"Utilisateur a le rôle: {role}")
```

#### 4. Tester les URLs RBAC

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class RBACURLsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

    def test_rbac_hub_requires_auth(self):
        """Hub RBAC doit nécessiter authentification"""
        response = self.client.get(reverse('rbac_hub'))
        self.assertEqual(response.status_code, 302)  # Redirection

    def test_rbac_hub_with_auth(self):
        """Hub RBAC doit être accessible après authentification"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('rbac_hub'))
        self.assertEqual(response.status_code, 200)

    def test_rbac_import_url_exists(self):
        """URL d'import doit exister"""
        url = reverse('rbac_import')
        self.assertEqual(url, '/admin/rbac/import/')

    def test_rbac_status_url_exists(self):
        """URL de statut doit exister"""
        url = reverse('rbac_status')
        self.assertEqual(url, '/admin/rbac/status/')
```

---

### Exemples JavaScript/TypeScript

#### 1. Faire une requête d'authentification

```javascript
// Login et obtenir le token JWT
async function login(username, password) {
    const response = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    if (response.ok) {
        const data = await response.json();
        const token = data.access;

        // Stocker le token
        localStorage.setItem('token', token);

        // Décoder le token pour voir le rôle (optionnel)
        const decoded = JSON.parse(atob(token.split('.')[1]));
        console.log('Rôle:', decoded.role);

        return token;
    } else {
        throw new Error('Login failed');
    }
}

// Utilisation
try {
    const token = await login('user@example.com', 'password123');
    console.log('Connecté avec token:', token.substring(0, 20) + '...');
} catch (error) {
    console.error(error);
}
```

#### 2. Faire une requête POST avec le token

```javascript
// Récupérer le token
function getToken() {
    return localStorage.getItem('token');
}

// Faire une requête authentifiée
async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };

    const options = {
        method: method,
        headers: headers
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`http://localhost:8000/api/data/${endpoint}`, options);

    if (response.status === 401) {
        // Token expiré, refaire login
        console.error('Token expiré');
        window.location.href = '/admin/login/';
    }

    return response.json();
}

// Utilisation
try {
    const sites = await apiRequest('sites?select=id,name');
    console.log('Sites:', sites);
} catch (error) {
    console.error('Erreur API:', error);
}
```

#### 3. Vérifier le rôle du token

```javascript
function decodeToken(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (error) {
        return null;
    }
}

function getUserRole() {
    const token = getToken();
    if (token) {
        const decoded = decodeToken(token);
        return decoded?.role || null;
    }
    return null;
}

function hasPermission(permission) {
    const role = getUserRole();
    // Implémenter la logique de vérification des permissions
    // Exemple: MRV_L1 peut R, MRV_L2 peut R+U, etc.
    return true; // À implémenter
}

// Utilisation
const userRole = getUserRole();
console.log('Rôle utilisateur:', userRole);

if (hasPermission('DELETE')) {
    // Afficher le bouton de suppression
}
```

#### 4. Faire une requête GET avec le token

```javascript
async function getDataFromPostgrest(table, filters = {}) {
    const token = getToken();

    // Construire la query string
    const queryParams = new URLSearchParams();
    queryParams.append('select', '*');

    Object.entries(filters).forEach(([key, value]) => {
        queryParams.append(key, `eq.${value}`);
    });

    const response = await fetch(
        `http://localhost:8000/api/data/${table}?${queryParams.toString()}`,
        {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    );

    if (response.ok) {
        return response.json();
    } else if (response.status === 403) {
        console.error('Permission denied - insufficient privileges');
    } else if (response.status === 401) {
        console.error('Unauthorized - token expired');
    }

    throw new Error(`HTTP ${response.status}`);
}

// Utilisation
try {
    const sites = await getDataFromPostgrest('sites', { name: 'Kinshasa' });
    console.log('Sites trouvés:', sites);
} catch (error) {
    console.error('Erreur:', error);
}
```

---

### Exemples cURL

#### 1. Obtenir un token

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'

# Réponse:
# {
#   "access": "eyJhbGc...",
#   "refresh": "eyJhbGc..."
# }
```

#### 2. Faire une requête PostgREST

```bash
TOKEN="eyJhbGc..."

curl -X GET http://localhost:8000/api/data/sites?select=id,name \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Réponse:
# [
#   { "id": 1, "name": "Site 1" },
#   { "id": 2, "name": "Site 2" }
# ]
```

#### 3. Créer une ressource

```bash
TOKEN="eyJhbGc..."

curl -X POST http://localhost:8000/api/data/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau projet",
    "description": "Description du projet"
  }'
```

#### 4. Mettre à jour une ressource

```bash
TOKEN="eyJhbGc..."

curl -X PATCH http://localhost:8000/api/data/projects/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Projet modifié"
  }'
```

#### 5. Supprimer une ressource

```bash
TOKEN="eyJhbGc..."

curl -X DELETE http://localhost:8000/api/data/projects/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Réponse: 204 No Content (succès)
```

---

### Exemples Django Templates

#### 1. Liens RBAC dans un template

```html
{% load admin_urls %}

<div class="rbac-menu">
    <h2>Gestion RBAC</h2>

    <ul>
        <li>
            <a href="{% url 'rbac_hub' %}">
                🏠 Hub central RBAC
            </a>
        </li>

        <li>
            <a href="{% url 'rbac_import' %}">
                📥 Importer la matrice
            </a>
        </li>

        <li>
            <a href="{% url 'rbac_status' %}">
                📊 Consulter le statut
            </a>
        </li>

        <li>
            <a href="{% url 'admin:core_userrole_changelist' %}">
                👤 Gérer les rôles
            </a>
        </li>
    </ul>
</div>
```

#### 2. Context dans une vue

```html
{% if user.is_staff %}
    <div class="admin-links">
        <a href="{{ rbac_hub }}">RBAC Hub</a>
        <a href="{{ rbac_import }}">Import RBAC</a>
        <a href="{{ rbac_status }}">Status RBAC</a>
    </div>
{% endif %}
```

---

### Tests complets

#### 1. Test d'intégration complète

```python
# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

class RBACIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )

    def test_rbac_workflow(self):
        # 1. Admin accède au hub
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('rbac_hub'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('RBAC', response.content.decode())

        # 2. Admin accède à l'import
        response = self.client.get(reverse('rbac_import'))
        self.assertEqual(response.status_code, 200)

        # 3. Admin accède au statut
        response = self.client.get(reverse('rbac_status'))
        self.assertEqual(response.status_code, 200)

        # 4. User non-admin ne peut pas accéder
        self.client.logout()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('rbac_hub'))
        self.assertEqual(response.status_code, 302)  # Redirection
```

---

**Exemples créés:** 2024
**Version:** 1.0
**Support:** Production Ready