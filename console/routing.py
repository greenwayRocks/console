from django.urls import path

from .consumers import ConsoleConsumer

ws_urlpatterns = [
    path('ws/console/', ConsoleConsumer.as_asgi())
]
