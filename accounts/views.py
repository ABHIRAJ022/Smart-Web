import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, UserUpdateForm 

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            otp = str(random.randint(100000, 999999))
            request.session['registration_data'] = request.POST.dict()
            request.session['otp'] = otp
            email = form.cleaned_data.get('email')
            try:
                send_mail(
                    "Verify your Health Dashboard Account",
                    f"Your verification code is: {otp}",
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                messages.success(request, f"Code sent to {email}.")
                return redirect('verify_otp')
            except Exception:
                messages.error(request, "Email delivery failed.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        user_entered_otp = request.POST.get('otp')
        real_otp = request.session.get('otp')
        user_data = request.session.get('registration_data')
        
        if user_entered_otp == real_otp:
            form = CustomUserCreationForm(user_data)
            if form.is_valid():
                user = form.save()
                request.session.flush()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"Welcome {user.username}!")
                return redirect('dashboard_home')
        messages.error(request, "Invalid OTP.")
    return render(request, 'accounts/verify_otp.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect('dashboard_home')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        messages.success(request, "Account deleted.")
        return redirect('login')
    return render(request, 'accounts/delete_account.html')