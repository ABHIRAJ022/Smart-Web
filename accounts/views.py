from django.shortcuts import render, redirect
from django.contrib.auth import login, logout # Added logout here
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserUpdateForm 

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard_home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    # This handles the form when the user clicks "Save"
    if request.method == 'POST':
        # instance=request.user tells Django to UPDATE the current user, not create a new one
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile') # Reloads the page to show new info
    else:
        # This pre-fills the form with their current info when they just load the page
        form = UserUpdateForm(instance=request.user)

    # Notice we pass 'form' to the template now
    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request) # Best practice: log them out before deleting to clear session cookies
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('login')
    return render(request, 'accounts/delete_account.html')