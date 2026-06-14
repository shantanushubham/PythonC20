"""
Local development — runs on your machine with docker-compose services.
"""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

LOG_LEVEL = "DEBUG"
