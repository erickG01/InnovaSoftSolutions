"""
Configuración WSGI para el proyecto InnovaSoftSolutions.

Expone el callable WSGI como una variable de nivel de módulo llamada ``application``.

Para más información sobre este archivo, consulta
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InnovaSoftSolutions.settings')

application = get_wsgi_application()