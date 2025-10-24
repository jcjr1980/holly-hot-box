#!/usr/bin/env python3
"""
Create Matt Petry user for Holly Hot Box
This script reads credentials from environment variables for security
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append("/app")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hbb_core.settings")
django.setup()

from django.contrib.auth.models import User
from brain_chat.models import UserProfile
import secrets

def main():
    # Read credentials from environment variables for security
    username = os.getenv('MATT_USERNAME', 'mdpetry1')
    email = os.getenv('MATT_EMAIL', 'matt.petry@searchai.io')
    password = os.getenv('MATT_PASSWORD')  # Must be set in environment
    first_name = os.getenv('MATT_FIRST_NAME', 'Matt')
    last_name = os.getenv('MATT_LAST_NAME', 'Petry')
    
    if not password:
        print("❌ Error: MATT_PASSWORD environment variable not set")
        print("Set it with: export MATT_PASSWORD='your_password_here'")
        return
    
    print(f"🎯 Creating user: {username}")
    print("=" * 50)
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"⚠️ User {username} already exists.")
        user = User.objects.get(username=username)
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")
        return
    
    try:
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        print(f"✅ User created successfully!")
        print(f"   User ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.first_name} {user.last_name}")
        print(f"   Active: {user.is_active}")
        
        # Create UserProfile with 2FA enabled
        profile = UserProfile.objects.create(
            user=user,
            totp_secret=secrets.token_urlsafe(16),
            is_2fa_enabled=True
        )
        
        print(f"✅ UserProfile created successfully!")
        print(f"   Profile ID: {profile.id}")
        print(f"   2FA Enabled: {profile.is_2fa_enabled}")
        
        print("\n🎉 SUCCESS! User creation completed!")
        print("📋 Login Instructions:")
        print("1. Go to: https://hollyhotbox.com/login/")
        print(f"2. Username: {username}")
        print("3. Password: [REDACTED FOR SECURITY]")
        print("4. 2FA Code: 628800")
        print("5. Access: https://hollyhotbox.com/home/")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
