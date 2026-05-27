import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Crée un superutilisateur dans la table 'users' personnalisée"

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email de l\'admin', default='admin@teraka.org')
        parser.add_argument('--password', type=str, help='Mot de passe', default='admin')
        parser.add_argument('--nom', type=str, help='Nom', default='Admin')
        parser.add_argument('--prenom', type=str, help='Prénom', default='')
        parser.add_argument('--genre', type=str, help='Genre (Masculin/Féminin)', default='Inconnu')
        parser.add_argument('--tel', type=str, help='Numéro de téléphone', default=None)
        parser.add_argument('--role', type=str, help='Code du rôle PostgreSQL (ex: Admin_L2)', default=None)
        parser.add_argument('--is_active', type=str, help='Statut actif (True/False)', default='True')

    def handle(self, *args, **options):
        from core.models_rbac import Role, UserRole

        email = options['email']
        password = options['password']
        nom = options['nom']
        prenom = options['prenom']
        genre = options['genre']
        tel = options['tel']
        role_code = options['role']
        is_active = options['is_active'].lower() == 'true'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"L'utilisateur {email} existe déjà. Mise à jour..."))
            user = User.objects.get(email=email)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = is_active
            user.nom = nom
            if prenom:
                user.prenom = prenom
            user.genre = genre
            if tel:
                user.num_tel = tel

            # Mise à jour du rôle legacy (colonne 'role')
            if role_code:
                user.role_name = role_code
            elif not user.role_name:
                user.role_name = 'Admin_L2' # Défaut pour éviter NOT NULL

            user.set_password(password)
            user.save()
        else:
            self.stdout.write(f"Création de {email}...")
            user = User.objects.create_superuser(
                email=email,
                password=password,
                nom=nom,
                prenom=prenom,
                genre=genre,
                num_tel=tel,
                is_active=is_active,
                role_name=role_code or 'Admin_L2', # Remplissage de la colonne legacy
                uuid_user=uuid.uuid4()
            )

        # Gestion du rôle (Relation UserRole pour le nouveau système)
        if role_code:
            Role.ensure_default_roles()
            try:
                role_obj = Role.objects.get(code=role_code)
                UserRole.objects.update_or_create(
                    user=user,
                    defaults={'role': role_obj}
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Rôle '{role_code}' assigné à {email}."))
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Le rôle '{role_code}' n'existe pas."))

        self.stdout.write(self.style.SUCCESS(f"✅ Superutilisateur {email} créé/mis à jour avec succès."))
        self.stdout.write(self.style.NOTICE("N'oubliez pas d'exécuter deployment_fix.sql avant si la table users n'a pas les colonnes is_staff/is_superuser."))
