import requests
import json # <-- Added to safely send data to the charts
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser, AccessControl
from ml_engine.predictor import predict_health_status
from urllib.parse import quote 

def fetch_thingspeak_data(channel_id, read_key, start_time=None, end_time=None):
    if not channel_id or not read_key:
        return [] # Return empty list instead of None
        
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}"
    
    if start_time and end_time:
        formatted_start = quote(start_time.replace('T', ' ') + ':00')
        formatted_end = quote(end_time.replace('T', ' ') + ':00')
        url += f"&start={formatted_start}&end={formatted_end}"
    else:
        # Fetch 30 data points for the live charts instead of just 1
        url += "&results=30"

    try:
        response = requests.get(url).json()
        if 'feeds' in response and len(response['feeds']) > 0:
            return response['feeds'] # Return the whole list
    except Exception as e:
        print("Error fetching ThingSpeak data:", e)
        return []
        
    return []

@login_required
def dashboard_home(request):
    user = request.user
    context = {'role': user.role}

    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    if user.role == 'patient':
        feeds = fetch_thingspeak_data(
            user.thingspeak_channel_id, 
            user.thingspeak_read_key,
            start_time=start_time,
            end_time=end_time
        )
        
        # Newest reading is at the end of the list
        latest_data = feeds[-1] if feeds else None
        
        prediction = None
        if latest_data:
            prediction = predict_health_status(latest_data)
        
        context['iot_data'] = latest_data
        context['prediction'] = prediction
        context['chart_data'] = json.dumps(feeds) # Send the whole list as JSON
        
        return render(request, 'dashboard/patient_dashboard.html', context)

    elif user.role in ['doctor', 'relative']:
        accessible_records = AccessControl.objects.filter(granted_to=user)
        patients = [record.patient for record in accessible_records]
        context['patients'] = patients
        return render(request, 'dashboard/doctor_dashboard.html', context)
        
    elif user.role == 'admin':
        context['all_users'] = CustomUser.objects.all()
        return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def view_patient_vitals(request, patient_id):
    patient = get_object_or_404(CustomUser, id=patient_id, role='patient')
    
    if request.user.role in ['doctor', 'relative']:
        has_access = AccessControl.objects.filter(patient=patient, granted_to=request.user).exists()
        if not has_access:
            messages.error(request, "You do not have permission to view this patient's vitals.")
            return redirect('dashboard_home')
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
    
    prediction = None
    if latest_data:
        prediction = predict_health_status(latest_data)
        
    context = {
        'patient': patient, 
        'iot_data': latest_data,
        'prediction': prediction,
        'chart_data': json.dumps(feeds), # Send the whole list as JSON for the doctor too!
    }
    
    return render(request, 'dashboard/patient_vitals.html', context)