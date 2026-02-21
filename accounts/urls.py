from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # --- Updated Informational Pages (Pointing to accounts/ folder) ---
    path('about/', TemplateView.as_view(template_name='accounts/about.html'), name='about'),
    path('vision/', TemplateView.as_view(template_name='accounts/vision.html'), name='vision'),
    path('contact/', views.contact, name='contact'), 
    
    # Google OAuth
    path('', include('allauth.urls')), 
]