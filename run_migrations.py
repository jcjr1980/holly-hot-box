#!/usr/bin/env python
"""
Migration runner script for Railway deployment
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def run_migrations():
    """Run Django migrations"""
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')
        django.setup()
        
        # Run migrations
        print("Running Django migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("Migrations completed successfully!")
        
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
