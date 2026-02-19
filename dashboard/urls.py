from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    # This new path handles the specific patient data screen
    path('patient/<int:patient_id>/vitals/', views.view_patient_vitals, name='view_patient_vitals'),
]