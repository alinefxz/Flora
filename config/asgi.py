import os

from django.core.asgi import get_asgi_application

# Mude aqui de 'flora.settings' para 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()