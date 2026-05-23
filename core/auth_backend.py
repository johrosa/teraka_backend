from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class UsersTableBackend(BaseBackend):
    """
    Backend d'authentification pour la table 'users' personnalisée.
    Gère le champ 'mot_de_passe' au lieu de 'password'.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get(email=username)
            # On vérifie le mot de passe stocké dans 'mot_de_passe'
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
