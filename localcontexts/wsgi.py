"""
WSGI config for localcontexts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localcontexts.settings')

application = get_wsgi_application()

# # Import your start_scheduler function
# from helpers.scheduler import start_scheduler

# # Call start_scheduler when the WSGI application is loaded
# start_scheduler()

