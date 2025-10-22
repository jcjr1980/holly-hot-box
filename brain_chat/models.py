"""
Holly Hot Box Models
Multi-LLM Brain Child System
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Project(models.Model):
    """Represents a research/work project with specific LLM configuration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True, help_text="Detailed project summary")
    
    # LLM Selection (JSON array of selected LLMs)
    selected_llms = models.JSONField(default=list, help_text="List of LLM names: gemini, deepseek, openai, claude, grok, huggingface")
    
    # Priority and organization
    priority = models.IntegerField(default=3, choices=[(i, str(i)) for i in range(1, 6)], help_text="1=Low, 5=Urgent")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Status tracking
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # AI-generated insights
    ai_summary = models.TextField(blank=True, help_text="Gemini-generated project summary")
    
    class Meta:
        ordering = ['-priority', '-updated_at']
    
    def __str__(self):
        return f"{self.name} (Priority {self.priority})"
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class ChatSession(models.Model):
    """Represents a chat session with the multi-LLM system"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Session types
    is_quickie = models.BooleanField(default=False, help_text="Quick one-off question")
    is_private = models.BooleanField(default=False, help_text="Private mode - temporary only")
    
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


class DiaryNote(models.Model):
    """Personal diary notes and reminders"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_notes')
    content = models.TextField()
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    mood = models.CharField(max_length=50, blank=True, help_text="Optional mood indicator")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Diary - {self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.content[:50]}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


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


class ProjectFile(models.Model):
    """Files uploaded to projects with AI summarization"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='project_files/%Y/%m/%d/')
    file_type = models.CharField(max_length=50)  # txt, json, pdf, docx, png, jpg
    file_size = models.IntegerField()
    original_content = models.TextField(blank=True, help_text="For text files")
    summary = models.TextField(blank=True, help_text="AI-generated summary")
    summarized_by = models.CharField(max_length=50, blank=True, help_text="Which LLM created summary")
    is_summarized = models.BooleanField(default=False)
    content_type = models.CharField(max_length=50, blank=True, help_text="contract, chat_history, technical, business, research, general")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.project.name})"


class RegistrationRequest(models.Model):
    """Store registration requests for new users"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.email}) - {self.status}"
