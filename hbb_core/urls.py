"""
URL configuration for Holly Hot Box (HBB) project.
Multi-LLM Brain Child System
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('brain_chat.urls')),
]
