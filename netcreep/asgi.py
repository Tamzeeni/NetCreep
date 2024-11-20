import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcreep.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from monitor.routing import websocket_urlpatterns

# Get the ASGI application early to report any import errors
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})