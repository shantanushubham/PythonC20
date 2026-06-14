import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_app.settings")

app = Celery("task_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(["task_app"], related_name="schedule")

app.conf.beat_schedule = {
    "my_task": {
        "task": "task_app.schedule.my_scheduled_function",
        "schedule": timedelta(seconds=30),
    }
}
