# import os

from django.core.wsgi import get_wsgi_application

from task_app.asgi import application

application = get_wsgi_application()