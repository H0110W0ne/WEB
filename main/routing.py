from django.urls import path

from .consumers import CommentConsumer

websocket_urlpatterns = [
    path('ws/comments/', CommentConsumer.as_asgi(), name='ws_comments'),
]
