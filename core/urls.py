from django.contrib import admin
from django.urls import path, include
from core.consumer import NotificationConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("researcher.urls")),
]

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi())
]