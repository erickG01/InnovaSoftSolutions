"""
Configuración ASGI para el proyecto InnovaSoftSolutions.

Expone el callable ASGI como una variable de nivel de módulo llamada ``application``.

Para más información sobre este archivo, consulta
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InnovaSoftSolutions.settings')

application = get_asgi_application()