from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Set up database - run migrations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database setup...'))
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', '--noinput')
        
        self.stdout.write(self.style.SUCCESS('Database setup complete!'))
