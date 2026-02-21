import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser, AccessControl
from ml_engine.predictor import predict_health_status
from urllib.parse import quote 

def fetch_thingspeak_data(channel_id, read_key, start_time=None, end_time=None):
    """
    Fetches historical or live data from ThingSpeak API.
    Handles datetime formatting for ThingSpeak-specific query requirements.
    """
    if not channel_id or not read_key:
        return []
        
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}"
    
    if start_time and end_time:
        # ThingSpeak requires %20 instead of T and needs seconds.
        # Example: '2023-10-27T14:30' -> '2023-10-27 14:30:00'
        formatted_start = quote(start_time.replace('T', ' ') + ':00')
        formatted_end = quote(end_time.replace('T', ' ') + ':00')
        url += f"&start={formatted_start}&end={formatted_end}"
    else:
        # Default to last 60 results for a better chart experience
        url += "&results=60"

    try:
        response = requests.get(url, timeout=7)
        response.raise_for_status() 
        data = response.json()
        return data.get('feeds', [])
    except Exception as e:
        print(f"ThingSpeak API Error: {e}")
        return []

@login_required
def dashboard_home(request):
    """
    Main entry point. Routes Patients to their vitals and 
    Doctors/Relatives to their patient list.
    """
    user = request.user
    
    if not user.role:
        messages.info(request, "Please complete your profile by selecting a role.")
        return redirect('profile')

    # --- PATIENT ROLE: Auto-load their own vitals ---
    if user.role == 'patient':
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        feeds = fetch_thingspeak_data(
            user.thingspeak_channel_id, 
            user.thingspeak_read_key,
            start_time=start_time,
            end_time=end_time
        )
        
        latest_data = feeds[-1] if feeds else None
        prediction = predict_health_status(latest_data) if latest_data else "No data available"
        
        context = {
            'role': user.role,
            'patient': user,
            'iot_data': latest_data,
            'prediction': prediction,
            'chart_data': json.dumps(feeds),
            'start_time': start_time,
            'end_time': end_time,
            'is_self_view': True,
        }
        return render(request, 'dashboard/patient_dashboard.html', context)

    # --- DOCTOR / RELATIVE ROLE: Load list of authorized patients ---
    elif user.role in ['doctor', 'relative']:
        accessible_records = AccessControl.objects.filter(granted_to=user).select_related('patient')
        patients = [record.patient for record in accessible_records]
        
        return render(request, 'dashboard/doctor_dashboard.html', {
            'role': user.role,
            'patients': patients
        })
        
    # --- ADMIN ROLE ---
    elif user.role == 'admin':
        all_users = CustomUser.objects.all().order_by('-date_joined')
        return render(request, 'dashboard/admin_dashboard.html', {
            'role': user.role,
            'all_users': all_users
        })

    return redirect('profile')

@login_required
def view_patient_vitals(request, patient_id):
    """
    Authorized view for Doctors/Relatives to see specific patient metrics.
    Includes security checks to prevent unauthorized data access.
    """
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    
    # Security Validation
    if request.user.role in ['doctor', 'relative']:
        has_access = AccessControl.objects.filter(patient=patient, granted_to=request.user).exists()
        if not has_access:
            messages.error(request, "Access Denied: Permission not granted by patient.")
            return redirect('dashboard_home')
    
    elif request.user.role == 'patient':
        if request.user.id != int(patient_id):
            messages.warning(request, "Access Denied: You cannot view other patients.")
            return redirect('dashboard_home')
    
    # Data Fetching
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    feeds = fetch_thingspeak_data(
        patient.thingspeak_channel_id, 
        patient.thingspeak_read_key,
        start_time=start_time,
        end_time=end_time
    )
    
    latest_data = feeds[-1] if feeds else None
    prediction = predict_health_status(latest_data) if latest_data else "Waiting for stream..."
        
    context = {
        'patient': patient, 
        'iot_data': latest_data,
        'prediction': prediction,
        'chart_data': json.dumps(feeds),
        'start_time': start_time,
        'end_time': end_time,
        'is_self_view': False,
    }
    
    return render(request, 'dashboard/patient_dashboard.html', context)