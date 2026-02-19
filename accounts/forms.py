from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'phone', 'iot_platform', 'thingspeak_channel_id', 'thingspeak_read_key', 'blynk_auth_token')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone')