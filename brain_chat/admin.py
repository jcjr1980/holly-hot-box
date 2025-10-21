"""
Holly Hot Box Admin Interface
"""
from django.contrib import admin
from .models import Project, ChatSession, ChatMessage, LLMResponse, ChatBackup, DiaryNote, UserProfile


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at', 'user')
    search_fields = ('name', 'description', 'tags')
    date_hierarchy = 'created_at'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'project', 'is_quickie', 'is_private', 'created_at', 'is_active')
    list_filter = ('is_active', 'is_quickie', 'is_private', 'created_at')
    search_fields = ('title', 'user__username', 'project__name')
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


@admin.register(DiaryNote)
class DiaryNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_preview', 'mood')
    list_filter = ('created_at', 'mood', 'user')
    search_fields = ('content', 'tags')
    date_hierarchy = 'created_at'
    
    def get_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    get_preview.short_description = 'Preview'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_2fa_enabled', 'last_login_ip', 'failed_login_attempts')
    list_filter = ('is_2fa_enabled',)
    search_fields = ('user__username',)
