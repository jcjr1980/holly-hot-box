"""
Holly Hot Box Models
Multi-LLM Brain Child System
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class ChatSession(models.Model):
    """Represents a chat session with the multi-LLM system"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # JSON metadata for quick LLM reference
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """Individual messages in a chat session"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    LLM_CHOICES = [
        ('openai', 'OpenAI GPT-4o'),
        ('gemini', 'Google Gemini'),
        ('deepseek', 'DeepSeek'),
        ('claude', 'Anthropic Claude'),
        ('grok', 'xAI Grok'),
        ('huggingface', 'Hugging Face'),
        ('multi', 'Multi-LLM Consensus'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    llm_provider = models.CharField(max_length=20, choices=LLM_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Token usage tracking
    tokens_used = models.IntegerField(default=0)
    
    # Response time tracking
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # JSON metadata for LLM-specific data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role} - {self.llm_provider or 'N/A'} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class LLMResponse(models.Model):
    """Stores individual LLM responses for consensus building"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='llm_responses')
    llm_provider = models.CharField(max_length=20)
    response_text = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.llm_provider} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class ChatBackup(models.Model):
    """30-second chat backups for recovery"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='backups')
    backup_data = models.JSONField()
    backup_timestamp = models.DateTimeField(auto_now_add=True)
    message_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-backup_timestamp']
    
    def __str__(self):
        return f"Backup - Session {self.session.id} - {self.backup_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class UserProfile(models.Model):
    """Extended user profile for 2FA"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hbb_profile')
    totp_secret = models.CharField(max_length=32, blank=True)
    is_2fa_enabled = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile - {self.user.username}"
