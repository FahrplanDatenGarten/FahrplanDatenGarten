"""
WSGI config for FahrplanDatenGarten project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import dotenv

dotenv.read_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.env'), override=True)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FahrplanDatenGarten.settings')

application = get_wsgi_application()
