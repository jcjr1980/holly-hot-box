#!/usr/bin/env python3
"""
Create initial users for Holly Hot Box
This command creates the required users if they don't exist.
"""
import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from brain_chat.models import UserProfile
import secrets

# Optional pyotp import - handle gracefully if not available
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None

class Command(BaseCommand):
    help = 'Create initial users for Holly Hot Box'

    def handle(self, *args, **options):
        self.stdout.write("🎯 Creating initial users for Holly Hot Box")
        self.stdout.write("=" * 50)
        
        # Create Matt Petry user
        self.create_matt_petry()
        
        # Create Sarah Wilson user
        self.create_sarah_wilson()
        
        self.stdout.write("\n🎉 Initial user creation completed!")

    def create_matt_petry(self):
        """Create Matt Petry user if it doesn't exist"""
        username = 'mdpetry1'
        
        # Check if Matt Petry already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"⚠️ User {username} already exists.")
            return
            
        try:
            # Create Matt Petry user
            user = User.objects.create_user(
                username='mdpetry1',
                email='matt.petry@searchai.io',
                password='Easton712022!!',
                first_name='Matt',
                last_name='Petry',
                is_active=True
            )
            
            # Create UserProfile with 2FA enabled
            profile = UserProfile.objects.create(
                user=user,
                totp_secret=secrets.token_urlsafe(16),
                is_2fa_enabled=True
            )
            
            self.stdout.write(f"✅ Created user: {username}")
            self.stdout.write(f"   Email: matt.petry@searchai.io")
            self.stdout.write(f"   Password: Easton712022!!")
            self.stdout.write(f"   2FA Code: 628800")
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating {username}: {e}")

    def create_sarah_wilson(self):
        """Create Sarah Wilson user if it doesn't exist"""
        username = 'sarah_wilson'
        
        # Check if Sarah Wilson already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"⚠️ User {username} already exists.")
            return
            
        try:
            # Create Sarah Wilson user
            user = User.objects.create_user(
                username='sarah_wilson',
                email='sarah@example.com',
                password='xK9mP2nQ8vR7',
                first_name='Sarah',
                last_name='Wilson',
                is_active=True
            )
            
            # Create UserProfile with 2FA disabled for testing
            profile = UserProfile.objects.create(
                user=user,
                totp_secret=secrets.token_urlsafe(16),
                is_2fa_enabled=False
            )
            
            self.stdout.write(f"✅ Created user: {username}")
            self.stdout.write(f"   Email: sarah@example.com")
            self.stdout.write(f"   Password: xK9mP2nQ8vR7")
            self.stdout.write(f"   2FA: Disabled")
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating {username}: {e}")
