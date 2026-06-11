import logging
from celery import shared_task
from celery.app import autoretry

logger = logging.getLogger(__name__)


@shared_task(max_retries=3, autoretry_for=(ConnectionError,), retry_backoff=True)
def process_event(self, message: str) -> str:
    """Consume a string event and log it."""
    logger.info("Received event: %s", message)
    # Connect to DB
    # Save in DB
    return f"processed: {message}"


# Pseudo Code
"""
    if transaction.status is not "PROCESSED":
        make-transaction
        transaction.status = "PROCESSED"
"""
