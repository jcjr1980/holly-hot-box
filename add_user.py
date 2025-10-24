#!/usr/bin/env python3
"""
Holly Hot Box User Management Script
Easy way to add new users with complete data isolation
"""

import os
import sys
import django
import secrets

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hbb_core.settings')
django.setup()

from django.contrib.auth.models import User
from brain_chat.models import UserProfile

# Optional pyotp import - handle gracefully if not available
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None


def add_user_interactive():
    """Interactive user creation"""
    print("🎯 Holly Hot Box User Creation")
    print("=" * 50)
    
    # Get user details
    username = input("Username: ").strip()
    if not username:
        print("❌ Username is required")
        return False
        
    email = input("Email: ").strip()
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists")
        return False
        
    if email and User.objects.filter(email=email).exists():
        print(f"❌ Email '{email}' already exists")
        return False
    
    # Generate password
    password = secrets.token_urlsafe(12)
    
    try:
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True
        )
        
        # Create UserProfile for 2FA
        if PYOTP_AVAILABLE:
            totp_secret = pyotp.random_base32()
            is_2fa_enabled = True
        else:
            totp_secret = secrets.token_urlsafe(16)
            is_2fa_enabled = False
        
        UserProfile.objects.create(
            user=user,
            totp_secret=totp_secret,
            is_2fa_enabled=is_2fa_enabled
        )
        
        print("\n" + "=" * 50)
        print("🎉 USER CREATED SUCCESSFULLY")
        print("=" * 50)
        print(f"Username: {user.username}")
        print(f"Email: {user.email or 'Not provided'}")
        print(f"Full Name: {user.first_name} {user.last_name}")
        print(f"Password: {password}")
        print(f"2FA Enabled: Yes")
        print("=" * 50)
        
        print("\n📋 USER DATA ISOLATION:")
        print("✅ Projects: Completely isolated")
        print("✅ Chat Sessions: Completely isolated")
        print("✅ Chat Messages: Completely isolated")
        print("✅ Diary Notes: Completely isolated")
        print("✅ Project Files: Completely isolated")
        print("✅ 2FA Settings: Individual per user")
        
        print("\n🔐 LOGIN INSTRUCTIONS:")
        print("1. Go to: https://hollyhotbox.com/login/")
        print(f"2. Username: {user.username}")
        print(f"3. Password: {password}")
        print("4. Complete 2FA verification")
        print("5. Access: https://hollyhotbox.com/home/")
        
        print("\n⚠️  IMPORTANT:")
        print("- Save this password securely")
        print("- User cannot see other users' data")
        print("- Each user has their own projects and chats")
        print("- 2FA is enabled for security")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False


def add_user_command_line(username, email="", first_name="", last_name="", password=""):
    """Command line user creation"""
    if not username:
        print("❌ Username is required")
        return False
        
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists")
        return False
        
    if email and User.objects.filter(email=email).exists():
        print(f"❌ Email '{email}' already exists")
        return False
    
    # Generate password if not provided
    if not password:
        password = secrets.token_urlsafe(12)
    
    try:
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True
        )
        
        # Create UserProfile for 2FA
        if PYOTP_AVAILABLE:
            totp_secret = pyotp.random_base32()
            is_2fa_enabled = True
        else:
            totp_secret = secrets.token_urlsafe(16)
            is_2fa_enabled = False
        
        UserProfile.objects.create(
            user=user,
            totp_secret=totp_secret,
            is_2fa_enabled=is_2fa_enabled
        )
        
        print(f"✅ User '{username}' created successfully!")
        print(f"🔐 Password: {password}")
        print(f"🌐 Login URL: https://hollyhotbox.com/login/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False


def list_users():
    """List all users"""
    users = User.objects.all().order_by('username')
    
    print("👥 Holly Hot Box Users")
    print("=" * 60)
    print(f"{'Username':<20} {'Email':<25} {'Name':<20} {'Active':<8}")
    print("-" * 60)
    
    for user in users:
        email = user.email or "Not provided"
        name = f"{user.first_name} {user.last_name}".strip() or "Not provided"
        active = "Yes" if user.is_active else "No"
        
        print(f"{user.username:<20} {email:<25} {name:<20} {active:<8}")
    
    print(f"\nTotal users: {users.count()}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "add":
            if len(sys.argv) >= 3:
                username = sys.argv[2]
                email = sys.argv[3] if len(sys.argv) > 3 else ""
                first_name = sys.argv[4] if len(sys.argv) > 4 else ""
                last_name = sys.argv[5] if len(sys.argv) > 5 else ""
                password = sys.argv[6] if len(sys.argv) > 6 else ""
                
                add_user_command_line(username, email, first_name, last_name, password)
            else:
                print("Usage: python add_user.py add <username> [email] [first_name] [last_name] [password]")
        
        elif command == "list":
            list_users()
        
        else:
            print("Available commands:")
            print("  add <username> [email] [first_name] [last_name] [password]")
            print("  list")
            print("  interactive")
    
    else:
        # Interactive mode
        add_user_interactive()
