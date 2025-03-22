import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import accounts.routing  # Import des routes WebSocket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "solar_monitoring.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # Gestion des requêtes HTTP
        "websocket": AuthMiddlewareStack(
            URLRouter(accounts.routing.websocket_urlpatterns)  # Gestion des WebSockets
        ),
    }
)
