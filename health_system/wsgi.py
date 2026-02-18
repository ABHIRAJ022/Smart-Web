import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_system.settings")

application = get_wsgi_application()

# Required for Vercel
app = application

# Auto-run migrations on deployment
try:
    print("Running migrations...")
    call_command('migrate', interactive=False)
    print("Migrations completed successfully.")
except Exception as e:
    print(f"Migration failed: {e}")