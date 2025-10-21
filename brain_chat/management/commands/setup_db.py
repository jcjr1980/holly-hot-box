from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Setup database by running migrations'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database...')
        
        try:
            # Check if we can connect to the database
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {e}'))
            return
        
        try:
            # Run migrations
            self.stdout.write('Running migrations...')
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            self.stdout.write(self.style.SUCCESS('Migrations completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Database setup completed!'))
