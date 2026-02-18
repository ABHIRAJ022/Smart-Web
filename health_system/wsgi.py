"""
WSGI config for health_system project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_system.settings")

application = get_wsgi_application()

# Required for Vercel
app = application
