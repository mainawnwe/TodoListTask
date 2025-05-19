# Implementing Real-Time Notifications with Django Channels

## Overview
This guide outlines the steps to add real-time notifications to your Django ToDo app using Django Channels and Redis.

## Steps

1. **Install Dependencies**
   - Install Django Channels and Redis support:
     ```
     pip install channels channels_redis
     ```
   - Ensure Redis server is installed and running.

2. **Update Django Settings**
   - Add `'channels'` to `INSTALLED_APPS`.
   - Set `ASGI_APPLICATION` to your project's ASGI application, e.g.:
     ```python
     ASGI_APPLICATION = 'todo.asgi.application'
     ```
   - Configure `CHANNEL_LAYERS` to use Redis:
     ```python
     CHANNEL_LAYERS = {
         'default': {
             'BACKEND': 'channels_redis.core.RedisChannelLayer',
             'CONFIG': {
                 'hosts': [('127.0.0.1', 6379)],
             },
         },
     }
     ```

3. **Create ASGI Application**
   - Create `asgi.py` in your project root (next to `settings.py`):
     ```python
     import os
     from channels.auth import AuthMiddlewareStack
     from channels.routing import ProtocolTypeRouter, URLRouter
     from django.core.asgi import get_asgi_application
     import myapp.routing

     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo.settings')

     application = ProtocolTypeRouter({
         "http": get_asgi_application(),
         "websocket": AuthMiddlewareStack(
             URLRouter(
                 myapp.routing.websocket_urlpatterns
             )
         ),
     })
     ```

4. **Create Routing for WebSocket**
   - In your app directory, create `routing.py`:
     ```python
     from django.urls import re_path
     from . import consumers

     websocket_urlpatterns = [
         re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
     ]
     ```

5. **Create Consumer**
   - In your app directory, create `consumers.py`:
     ```python
     import json
     from channels.generic.websocket import AsyncWebsocketConsumer

     class NotificationConsumer(AsyncWebsocketConsumer):
         async def connect(self):
             self.group_name = f'user_{self.scope["user"].id}'
             await self.channel_layer.group_add(self.group_name, self.channel_name)
             await self.accept()

         async def disconnect(self, close_code):
             await self.channel_layer.group_discard(self.group_name, self.channel_name)

         async def send_notification(self, event):
             message = event['message']
             await self.send(text_data=json.dumps({'message': message}))
     ```

6. **Send Notifications**
   - Use Django signals or Celery tasks to send notifications to the user's group:
     ```python
     from asgiref.sync import async_to_sync
     from channels.layers import get_channel_layer

     channel_layer = get_channel_layer()
     async_to_sync(channel_layer.group_send)(
         f'user_{user.id}',
         {
             'type': 'send_notification',
             'message': 'You have a task due soon!',
         }
     )
     ```

7. **Update Frontend**
   - Replace polling with WebSocket connection in your JavaScript:
     ```javascript
     const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

     socket.onmessage = function(e) {
       const data = JSON.parse(e.data);
       showNotification(data.message);
     };
     ```

## Notes
- Ensure Redis is running and accessible.
- Use secure WebSocket (wss://) in production.
- Handle authentication and permissions carefully.
- Test thoroughly for connection handling and reconnection logic.

This setup will provide real-time task notifications to users in your Django app.
