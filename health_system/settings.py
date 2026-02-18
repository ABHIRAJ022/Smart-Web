import os
from pathlib import Path
import dj_database_url

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-this-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]  # Change to your Vercel domain in production

# Application Definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom Apps
    "accounts",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files for Vercel
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "health_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "health_system.wsgi.application"

# ===============================
# DATABASE CONFIGURATION
# ===============================
# Uses Neon PostgreSQL if DATABASE_URL is set in environment (Vercel).
# Otherwise, it falls back to a local SQLite database for Codespace development.
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('postgresql://neondb_owner:npg_dwEbRjP24NKi@ep-crimson-river-a1v2lmwe-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===============================
# Custom User Model
# ===============================
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_REDIRECT_URL = "dashboard_home"
LOGOUT_REDIRECT_URL = "login"

# ===============================
# Static Files
# ===============================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===============================
# Internationalization
# ===============================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default Primary Key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"