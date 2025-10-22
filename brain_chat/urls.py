"""
Holly Hot Box URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.coming_soon_view, name='coming_soon'),  # Homepage is now Coming Soon
    path('home/', views.home, name='home'),  # Actual app home for logged in users
    path('new-chat/', views.new_chat, name='new_chat'),
    path('project/create/', views.create_project_view, name='create_project'),
    path('chat/', views.chat_home, name='chat_home'),
    path('login/', views.login_view, name='login'),
    path('login/2fa/', views.login_2fa_view, name='login_2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/success/', views.register_success_view, name='register_success'),
    path('send-message/', views.send_message, name='send_message'),
    path('new-session/', views.new_session, name='new_session'),
    path('session/<int:session_id>/', views.load_session, name='load_session'),
    path('session/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    
    # Projects
    path('projects/', views.get_projects, name='get_projects'),
    path('projects/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/update/', views.update_project, name='update_project'),
    path('project/<int:project_id>/upload-files/', views.upload_project_files, name='upload_project_files'),
    path('project/<int:project_id>/file/<int:file_id>/delete/', views.delete_project_file, name='delete_project_file'),
    
    # Chats
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    
    # Diary
    path('diary/', views.get_diary_notes, name='get_diary_notes'),
    path('diary/create/', views.create_diary_note, name='create_diary_note'),
    
    # System
    path('health/', views.health_check_view, name='health_check'),
    path('setup-db/', views.setup_database, name='setup_database'),
    path('test-llms/', views.test_llms, name='test_llms'),
    path('send-sms/', views.send_sms_notification, name='send_sms'),
]

