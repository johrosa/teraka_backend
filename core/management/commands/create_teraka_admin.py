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

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nom = options['nom']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"L'utilisateur {email} existe déjà. Mise à jour du statut superuser..."))
            user = User.objects.get(email=email)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
        else:
            self.stdout.write(f"Création de {email}...")
            User.objects.create_superuser(
                email=email,
                password=password,
                nom=nom,
                uuid_user=uuid.uuid4()
            )

        self.stdout.write(self.style.SUCCESS(f"✅ Superutilisateur {email} créé/mis à jour avec succès."))
        self.stdout.write(self.style.NOTICE("N'oubliez pas d'exécuter deployment_fix.sql avant si la table users n'a pas les colonnes is_staff/is_superuser."))
