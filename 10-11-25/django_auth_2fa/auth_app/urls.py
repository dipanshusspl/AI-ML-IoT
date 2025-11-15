from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('backup-codes/', views.backup_codes, name='backup_codes'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('dashboard/', views.dashboard, name='dashboard'),
]