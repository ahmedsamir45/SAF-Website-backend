"""
Django settings for SAF_backend project.
"""

from pathlib import Path
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Port configuration
PORT = os.environ.get('PORT', '8000')  # Default to 12083 if not set

# Try to import dj_database_url, but don't fail if it's not installed
try:
    import dj_database_url
    DATABASE_URL_AVAILABLE = True
except ImportError:
    DATABASE_URL_AVAILABLE = False

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Print debug info
print(f"Loaded .env file from: {env_path}")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
print(f"DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL')}")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-unsafe')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# Base URL for generating absolute URLs
# Production domain
DEFAULT_URL = 'https://safstudentactivtiesfamily.com'
BASE_URL = os.getenv('BASE_URL', DEFAULT_URL)

# Parse ALLOWED_HOSTS from environment variable or default to the domain
ALLOWED_HOSTS = ["*"]

# -------------------------------------------------------------------
# CORS SETTINGS
# -------------------------------------------------------------------
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
# Security settings
# CSRF_TRUSTED_ORIGINS = [
#     'https://safstudentactivtiesfamily.com',
#     'https://www.safstudentactivtiesfamily.com',
# ]

# Security Headers
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True



DEFAULT_CSRF_ORIGINS = [
    '*',
    'http://localhost',
    'http://127.0.0.1',
]
DEFAULT_CORS_ORIGINS = [
    'https://saf-website-backend-backend-only-f6d2c1c.kuberns.cloud',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]




CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken', 'Authorization']
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# -------------------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'phonenumber_field',
    'djoser',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',  # For API documentation
    'django_filters',
    'whitenoise.runserver_nostatic',

    # Local apps
    'activities',
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Keep this near the top
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------------------------------------------
# URLS & WSGI
# -------------------------------------------------------------------
ROOT_URLCONF = 'SAF_backend.urls'
WSGI_APPLICATION = 'SAF_backend.wsgi.application'

# -------------------------------------------------------------------
# DATABASE (SQLite)
# Database Configuration
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Default to PostgreSQL configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    # Default PostgreSQL configuration if DATABASE_URL is not set
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'saf_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 5,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
            },
            'CONN_MAX_AGE': 600,  # 10 minutes persistent connections
        }
    }
else:
    # Use DATABASE_URL if provided (for production/Heroku/etc.)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=os.getenv('DB_SSL', 'False').lower() == 'true'
        )
    }
    
    # Add PostgreSQL-specific settings if using PostgreSQL
    if 'postgresql' in DATABASE_URL or 'postgres' in DATABASE_URL:
        DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {}) | {
            'connect_timeout': 5,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
        }

# Test database configuration (if needed)
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['default']['NAME'] = ':memory:'

# -------------------------------------------------------------------
# CUSTOM USER MODEL
# -------------------------------------------------------------------
AUTH_USER_MODEL = 'activities.User'

# -------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# -------------------------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'subscription': '5/hour',  # For newsletter subscription
        'confirm_subscription': '10/hour',  # For confirmation attempts
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# -------------------------------------------------------------------
# SIMPLE JWT SETTINGS
# -------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'AUTH_COOKIE': 'access',
    'AUTH_COOKIE_SECURE': os.getenv('COOKIE_SECURE', 'False') == 'True',
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

# -------------------------------------------------------------------
# DJOSER SETTINGS
# -------------------------------------------------------------------
DJOSER = {
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SERIALIZERS': {
        'user_create': 'activities.serializers.UserCreateWithProfileSerializer',
        'user': 'activities.serializers.UserSerializer',
        'current_user': 'activities.serializers.UserSerializer',
        'user_delete': 'djoser.serializers.UserSerializer',
    },
    'TOKEN_MODEL': None,
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
}

# -------------------------------------------------------------------
# SPECTACULAR SETTINGS (API Documentation)
# -------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'SAF Backend API',
    'DESCRIPTION': 'API documentation for SAF Backend',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SERVE_PUBLIC': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayRequestDuration': True,
    },
    'SECURITY': [
        {
            'Bearer': []
        }
    ],
    'TAGS_SORTER': 'alpha',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',
}

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Create static directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Create media directory if it doesn't exist
# Ensure the media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# File upload permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# -------------------------------------------------------------------
# EMAIL CONFIGURATION
# -------------------------------------------------------------------
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'safstudentactivtiesfamily.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))  # 465 for SSL, 587 for TLS
EMAIL_USE_SSL = True  # Use SSL for port 465
# EMAIL_USE_TLS = True  # Uncomment this and comment above if using port 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'info@safstudentactivtiesfamily.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@safstudentactivtiesfamily.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL  # For error messages
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@safstudentactivtiesfamily.com')

# -------------------------------------------------------------------
# DEFAULTS
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------
import os
from pathlib import Path

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
