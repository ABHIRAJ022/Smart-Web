from django.urls import path
from . import views

urlpatterns = [
    # General dashboard entrance
    path('', views.dashboard_home, name='dashboard_home'),
    
    # Specific view for doctors/relatives to see a patient's historical data
    path('patient/<int:patient_id>/vitals/', views.view_patient_vitals, name='view_patient_vitals'),
]