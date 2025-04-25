# myproject/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat_module.routing  # ایمپورت routing اپ چت

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop_product.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_module.routing.websocket_urlpatterns
        )
    ),
})