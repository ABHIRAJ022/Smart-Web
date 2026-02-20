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
    Handles URL encoding for time-filtered queries.
    """
    if not channel_id or not read_key:
        return []
        
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}"
    
    if start_time and end_time:
        # Convert HTML5 datetime-local format (T) to ThingSpeak format (space)
        formatted_start = quote(start_time.replace('T', ' ') + ':00')
        formatted_end = quote(end_time.replace('T', ' ') + ':00')
        url += f"&start={formatted_start}&end={formatted_end}"
    else:
        # Default to last 30 readings to keep charts performant
        url += "&results=30"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        return data.get('feeds', [])
    except Exception as e:
        print(f"ThingSpeak API Error: {e}")
        return []

@login_required
def dashboard_home(request):
    """
    Main entry point for the dashboard. 
    Routes users based on their role: Patient, Doctor, Relative, or Admin.
    """
    user = request.user
    
    # Check for incomplete profiles (Crucial for Google Social Login users)
    if not user.role:
        messages.info(request, "Please complete your profile by selecting a role.")
        return redirect('profile')

    context = {'role': user.role}
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    # --- PATIENT ROLE ---
    if user.role == 'patient':
        feeds = fetch_thingspeak_data(
            user.thingspeak_channel_id, 
            user.thingspeak_read_key,
            start_time=start_time,
            end_time=end_time
        )
        
        latest_data = feeds[-1] if feeds else None
        prediction = predict_health_status(latest_data) if latest_data else "No data available"
        
        context.update({
            'iot_data': latest_data,
            'prediction': prediction,
            'chart_data': json.dumps(feeds), # Passed to Chart.js in the template
            'start_time': start_time,
            'end_time': end_time,
        })
        return render(request, 'dashboard/patient_dashboard.html', context)

    # --- DOCTOR / RELATIVE ROLE ---
    elif user.role in ['doctor', 'relative']:
        # Fetch patients who have explicitly granted access via AccessControl model
        accessible_records = AccessControl.objects.filter(granted_to=user).select_related('patient')
        patients = [record.patient for record in accessible_records]
        context['patients'] = patients
        return render(request, 'dashboard/doctor_dashboard.html', context)
        
    # --- ADMIN ROLE ---
    elif user.role == 'admin':
        context['all_users'] = CustomUser.objects.all().order_by('-date_joined')
        return render(request, 'dashboard/admin_dashboard.html', context)

    return redirect('profile')

@login_required
def view_patient_vitals(request, patient_id):
    """
    Detailed view for Doctors/Relatives to see a specific patient's data.
    Includes security checks to prevent unauthorized data access.
    """
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    
    # Security: Ensure current user has permission to view this specific patient
    if request.user.role in ['doctor', 'relative']:
        has_access = AccessControl.objects.filter(patient=patient, granted_to=request.user).exists()
        if not has_access:
            messages.error(request, "You do not have permission to view this patient's data.")
            return redirect('dashboard_home')
    
    # Patients can only view their own vitals through this view
    elif request.user.role == 'patient' and request.user.id != patient.id:
        return redirect('dashboard_home')

    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    feeds = fetch_thingspeak_data(
        patient.thingspeak_channel_id, 
        patient.thingspeak_read_key,
        start_time=start_time,
        end_time=end_time
    )
    
    latest_data = feeds[-1] if feeds else None
    prediction = predict_health_status(latest_data) if latest_data else "Waiting for data..."
        
    context = {
        'patient': patient, 
        'iot_data': latest_data,
        'prediction': prediction,
        'chart_data': json.dumps(feeds),
        'start_time': start_time,
        'end_time': end_time,
    }
    return render(request, 'dashboard/patient_vitals.html', context)