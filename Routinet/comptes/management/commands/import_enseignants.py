import csv
from django.contrib.auth.models import User, Group
from comptes.models import Profile  # Adjust if your profile model is elsewhere
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Import enseignants from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                username = row['username']
                password = row['password']
                first_name = row['first_name']
                last_name = row['last_name']
                email = row['email']
                telephone = row['telephone']
                date_naissance = row['date_naissance']
                # Create user
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                    }
                )
                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'User already exists: {username}'))
                # Set role/group if needed
                group, _ = Group.objects.get_or_create(name='Enseignant')
                user.groups.add(group)
                # Update profile fields if you have a Profile model
                if hasattr(user, 'profile'):
                    user.profile.telephone = telephone
                    user.profile.role = 'enseignant'
                    try:
                        user.profile.date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d').date()
                    except Exception:
                        user.profile.date_naissance = None
                    user.profile.save()
