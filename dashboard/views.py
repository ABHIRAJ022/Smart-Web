import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, AccessControl
from ml_engine.predictor import predict_health_status

def fetch_thingspeak_data(channel_id, read_key):
    if not channel_id or not read_key:
        return None
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}&results=1"
    try:
        response = requests.get(url).json()
        if 'feeds' in response and len(response['feeds']) > 0:
            return response['feeds'][0] # Returns latest row (Temp, Smoke, Alcohol, etc.)
    except:
        return None
    return None

@login_required
def dashboard_home(request):
    user = request.user
    context = {'role': user.role}

    if user.role == 'patient':
        # Fetch Patient's own IoT Data
        latest_data = fetch_thingspeak_data(user.thingspeak_channel_id, user.thingspeak_read_key)
        prediction = None
        if latest_data:
            # Pass to ML engine
            prediction = predict_health_status(latest_data)
        
        context['iot_data'] = latest_data
        context['prediction'] = prediction
        return render(request, 'dashboard/patient_dashboard.html', context)

    elif user.role in ['doctor', 'relative']:
        # Fetch patients who granted access to this doctor/relative
        accessible_records = AccessControl.objects.filter(granted_to=user)
        patients = [record.patient for record in accessible_records]
        context['patients'] = patients
        return render(request, 'dashboard/doctor_dashboard.html', context)
        
    elif user.role == 'admin':
        context['all_users'] = CustomUser.objects.all()
        return render(request, 'dashboard/admin_dashboard.html', context)