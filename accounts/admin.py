from django.contrib import admin
from .models import CustomUser, AccessControl

admin.site.register(CustomUser)
admin.site.register(AccessControl)