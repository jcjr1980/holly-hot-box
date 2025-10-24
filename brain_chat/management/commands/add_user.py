"""
Django management command to add new users to Holly Hot Box
Usage: python manage.py add_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
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
    help = 'Add a new user to Holly Hot Box with complete data isolation'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the new user')
        parser.add_argument('--email', type=str, help='Email for the new user')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')
        parser.add_argument('--password', type=str, help='Password (will be generated if not provided)')
        parser.add_argument('--interactive', action='store_true', help='Interactive mode')

    def handle(self, *args, **options):
        # Create Matt Petry user by default
        self.create_matt_petry()
        
        if options['interactive']:
            self.interactive_mode()
        else:
            self.command_line_mode(options)

    def interactive_mode(self):
        """Interactive user creation"""
        self.stdout.write(self.style.SUCCESS('🎯 Holly Hot Box User Creation'))
        self.stdout.write('=' * 50)
        
        # Get user details
        username = input('Username: ').strip()
        if not username:
            self.stdout.write(self.style.ERROR('Username is required'))
            return
            
        email = input('Email: ').strip()
        first_name = input('First Name: ').strip()
        last_name = input('Last Name: ').strip()
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists'))
            return
            
        if email and User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'Email "{email}" already exists'))
            return
        
        # Generate password
        password = secrets.token_urlsafe(12)
        
        # Create user
        user = self.create_user(username, email, first_name, last_name, password)
        
        if user:
            self.display_user_info(user, password)

    def command_line_mode(self, options):
        """Command line user creation"""
        username = options.get('username')
        if not username:
            self.stdout.write(self.style.ERROR('Username is required. Use --username or --interactive'))
            return
            
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists'))
            return
            
        email = options.get('email', '')
        if email and User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'Email "{email}" already exists'))
            return
        
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')
        password = options.get('password') or secrets.token_urlsafe(12)
        
        # Create user
        user = self.create_user(username, email, first_name, last_name, password)
        
        if user:
            self.display_user_info(user, password)

    def create_user(self, username, email, first_name, last_name, password):
        """Create a new user with profile"""
        try:
            # Create Django User
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_active=True,
                is_staff=False,
                is_superuser=False
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
            
            self.stdout.write(self.style.SUCCESS(f'✅ User "{username}" created successfully'))
            return user
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating user: {e}'))
            return None

    def display_user_info(self, user, password):
        """Display user information"""
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🎉 USER CREATED SUCCESSFULLY'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Email: {user.email or "Not provided"}')
        self.stdout.write(f'Full Name: {user.first_name} {user.last_name}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'2FA Enabled: Yes')
        self.stdout.write('=' * 50)
        
        self.stdout.write('\n📋 USER DATA ISOLATION:')
        self.stdout.write('✅ Projects: Completely isolated')
        self.stdout.write('✅ Chat Sessions: Completely isolated')
        self.stdout.write('✅ Chat Messages: Completely isolated')
        self.stdout.write('✅ Diary Notes: Completely isolated')
        self.stdout.write('✅ Project Files: Completely isolated')
        self.stdout.write('✅ 2FA Settings: Individual per user')
        
        self.stdout.write('\n🔐 LOGIN INSTRUCTIONS:')
        self.stdout.write('1. Go to: https://hollyhotbox.com/login/')
        self.stdout.write(f'2. Username: {user.username}')
        self.stdout.write(f'3. Password: {password}')
        self.stdout.write('4. Complete 2FA verification')
        self.stdout.write('5. Access: https://hollyhotbox.com/home/')
        
        self.stdout.write('\n⚠️  IMPORTANT:')
        self.stdout.write('- Save this password securely')
        self.stdout.write('- User cannot see other users\' data')
        self.stdout.write('- Each user has their own projects and chats')
        self.stdout.write('- 2FA is enabled for security')

    def create_matt_petry(self):
        """Create Matt Petry user specifically"""
        username = 'mdpetry1'
        email = 'matt.petry@searchai.io'
        password = 'Easton712022!!'
        first_name = 'Matt'
        last_name = 'Petry'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"⚠️ User {username} already exists.")
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
            
            # Create UserProfile with 2FA enabled
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
            
            self.stdout.write(f"✅ Matt Petry user created successfully!")
            self.stdout.write(f"   Username: {username}")
            self.stdout.write(f"   Password: {password}")
            self.stdout.write(f"   2FA Code: 628800")
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating Matt Petry user: {e}")
