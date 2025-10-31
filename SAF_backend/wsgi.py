"""
WSGI config for SAF_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAF_backend.settings')

# This application object is used by the development server and any WSGI server
def get_wsgi_application():
    # Import here to ensure settings are loaded first
    from django.core.wsgi import get_wsgi_application as django_get_wsgi_application
    return django_get_wsgi_application()

# Create the WSGI application
application = get_wsgi_application()

