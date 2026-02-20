from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    
    # Add this line to handle Google/Social login routing
    path('accounts/', include('allauth.urls')), 
]