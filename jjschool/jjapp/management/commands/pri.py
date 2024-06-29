from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from jjapp.models import CustomUser, Principal  # Adjust the import according to your app's structure

class Command(BaseCommand):
    help = 'Create or update the principal user'

    def handle(self, *args, **kwargs):
        try:
            principal_user = CustomUser.objects.get(username='hyy', role='principal')
            principal_user.delete()
        except CustomUser.DoesNotExist:
            pass  # If no Principal found, do nothing

        # Create a new Principal user with username and hashed password
        password = 'hyy'  # The password you want to set
        hashed_password = make_password(password)

        user = CustomUser.objects.create(username='hyy', password=hashed_password, role='principal')

        # Optionally, create the Principal profile with other details
        principal = Principal.objects.create(user=user, phone_number='4854873488167')

        # Print a confirmation message
        self.stdout.write(self.style.SUCCESS(f"Principal user 'hyy' created with password: {password}"))