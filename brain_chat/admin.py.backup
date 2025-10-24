"""
User Management Admin Interface for Holly Hot Box
Provides easy user creation and management
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from brain_chat.models import UserProfile, RegistrationRequest, Project, ChatSession
import secrets

# Optional pyotp import - handle gracefully if not available
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('totp_secret', 'is_2fa_enabled', 'last_login_ip', 'failed_login_attempts', 'locked_until')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'user_stats')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def user_stats(self, obj):
        """Display user statistics"""
        projects_count = Project.objects.filter(user=obj).count()
        chats_count = ChatSession.objects.filter(user=obj).count()
        return format_html(
            '<span style="color: #00bfff;">📁 {} projects</span><br>'
            '<span style="color: #9333ea;">💬 {} chats</span>',
            projects_count, chats_count
        )
    user_stats.short_description = 'User Stats'
    


class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    actions = ['approve_registrations', 'reject_registrations']
    
    def approve_registrations(self, request, queryset):
        """Approve selected registration requests"""
        approved_count = 0
        for registration in queryset:
            if registration.status == 'pending':
                # Create user account
                username = registration.email.split('@')[0]  # Use email prefix as username
                password = secrets.token_urlsafe(12)
                
                # Ensure username is unique
                original_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=registration.email,
                        first_name=registration.name.split()[0] if registration.name else '',
                        last_name=' '.join(registration.name.split()[1:]) if len(registration.name.split()) > 1 else '',
                        password=password,
                        is_active=True
                    )
                    
                    # Create UserProfile
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
                    
                    registration.status = 'approved'
                    registration.save()
                    approved_count += 1
                    
                    messages.success(request, f'✅ Created user "{username}" with password: {password}')
                    
                except Exception as e:
                    messages.error(request, f'❌ Error creating user for {registration.email}: {e}')
        
        if approved_count > 0:
            messages.success(request, f'✅ Approved {approved_count} registration(s)')
    
    approve_registrations.short_description = "Approve and create user accounts"
    
    def reject_registrations(self, request, queryset):
        """Reject selected registration requests"""
        updated = queryset.update(status='rejected')
        messages.success(request, f'❌ Rejected {updated} registration(s)')
    
    reject_registrations.short_description = "Reject registration requests"
    
    
    def registration_requests_view(self, request):
        """View registration requests"""
        requests = RegistrationRequest.objects.all().order_by('-created_at')
        return render(request, 'admin/registration_requests.html', {'requests': requests})


# Register the custom admin classes
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(RegistrationRequest, RegistrationRequestAdmin)