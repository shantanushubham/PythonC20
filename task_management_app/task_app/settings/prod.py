"""
Production — live app serving customers.
"""

import os

from .base import *  # noqa: F403

DEBUG = False

if SECRET_KEY == "django-insecure-dev-only-change-in-prod":  # noqa: F405
    raise ValueError("Set DJANGO_SECRET_KEY for production.")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ValueError("Set DJANGO_ALLOWED_HOSTS for production.")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() in ("1", "true", "yes")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
