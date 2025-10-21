"""
Holly Hot Box URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('login/', views.login_view, name='login'),
    path('login/2fa/', views.login_2fa_view, name='login_2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('send-message/', views.send_message, name='send_message'),
    path('new-session/', views.new_session, name='new_session'),
    path('session/<int:session_id>/', views.load_session, name='load_session'),
    path('session/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    
    # Projects
    path('projects/', views.get_projects, name='get_projects'),
    path('projects/create/', views.create_project, name='create_project'),
    
    # Diary
    path('diary/', views.get_diary_notes, name='get_diary_notes'),
    path('diary/create/', views.create_diary_note, name='create_diary_note'),
    
    # System
    path('health/', views.health_check, name='health_check'),
    path('setup-db/', views.setup_database, name='setup_database'),
]

