"""
Producer script — enqueues a string event via Celery.

Usage:
    python produce_event.py "hello world"
    python produce_event.py          # uses a default message
"""
import sys
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_app.settings')
django.setup()

from task_app.tasks import process_event  # noqa: E402 — must come after django.setup()

if __name__ == '__main__':
    message = sys.argv[1] if len(sys.argv) > 1 else "default event message"
    result = process_event.delay(message)
    print(f"Event enqueued. Task id: {result.id}")
