"""
Holly Hot Box Admin Interface
"""
from django.contrib import admin
from .models import ChatSession, ChatMessage, LLMResponse, ChatBackup, UserProfile


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'user__username')
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'llm_provider', 'tokens_used', 'created_at')
    list_filter = ('role', 'llm_provider', 'created_at')
    search_fields = ('content', 'session__title')
    date_hierarchy = 'created_at'


@admin.register(LLMResponse)
class LLMResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'llm_provider', 'tokens_used', 'response_time_ms', 'created_at')
    list_filter = ('llm_provider', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(ChatBackup)
class ChatBackupAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'message_count', 'backup_timestamp')
    list_filter = ('backup_timestamp',)
    date_hierarchy = 'backup_timestamp'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_2fa_enabled', 'last_login_ip', 'failed_login_attempts')
    list_filter = ('is_2fa_enabled',)
    search_fields = ('user__username',)
