# import os

from django.core.asgi import get_asgi_application

from task_app.asgi import application

application = get_asgi_application()