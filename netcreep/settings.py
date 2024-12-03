import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "True") == "True"

# Hosts and CORS Configuration
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "SECURITY_CORS_ALLOWED_ORIGINS", "http://localhost:8000"
    ).split(",")
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "SECURITY_CSRF_TRUSTED_ORIGINS", "http://localhost:8000"
    ).split(",")
    if origin.strip()
]

# Application Definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "channels",
    "corsheaders",
    "django_ratelimit",
    "axes",
    "defender",
    # Project apps
    "monitor",
    "netcreep",
]

# Middleware Configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Database Configuration
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "netcreep_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "root"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Email Configuration
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.hostinger.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "NetCreep Monitoring")

# Validate critical email configurations
if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    import warnings

    warnings.warn(
        "Email configuration is incomplete. Some email functionalities may not work.",
        RuntimeWarning,
    )

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": os.getenv("LOGGING_LEVEL", "WARNING"),
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "app.log"),
        },
        "console": {
            "level": os.getenv("LOGGING_LEVEL", "WARNING"),
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": os.getenv("LOGGING_LEVEL", "WARNING"),
            "propagate": True,
        },
        "monitor": {
            "handlers": ["file", "console"],
            "level": os.getenv("LOGGING_LEVEL", "WARNING"),
            "propagate": True,
        },
    },
}

# Rate Limiting Configuration
RATELIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 50))
RATELIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", 3600))

# Network Capture Settings
CAPTURE_INTERFACES = os.getenv("CAPTURE_INTERFACES", "WiFi,Ethernet").split(",")
MAX_PACKET_STORE = int(os.getenv("MAX_PACKET_STORE", 50000))
PACKET_CLEANUP_INTERVAL = int(os.getenv("PACKET_CLEANUP_INTERVAL", 7200))

# IP Whitelisting
ALLOWED_IP_RANGES = os.getenv("ALLOWED_IP_RANGES", "127.0.0.1/32,192.168.1.0/24").split(
    ","
)

# Optional Security Enhancements (always on)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# Static and Media Files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Channels Configuration
ASGI_APPLICATION = "netcreep.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Root URL Configuration
ROOT_URLCONF = "netcreep.urls"

# WSGI Application
WSGI_APPLICATION = "netcreep.wsgi.application"

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Default Primary Key Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Update port if necessary
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
