"""
Dev / E2E — shared remote environment for building and testing features.
"""

import os

from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "dev.example.com").split(",")
    if host.strip()
]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
