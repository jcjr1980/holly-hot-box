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
    path('health/', views.health_check, name='health_check'),
    path('setup-db/', views.setup_database, name='setup_database'),
]

