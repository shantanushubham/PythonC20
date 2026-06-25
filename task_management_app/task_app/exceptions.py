import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

# Built-in exceptions mapped to (HTTP status, client-facing message).
EXCEPTION_MAP = {
    ZeroDivisionError: (status.HTTP_400_BAD_REQUEST, "Cannot divide by zero"),
    ValueError: (status.HTTP_400_BAD_REQUEST, "Invalid value provided"),
    TypeError: (status.HTTP_400_BAD_REQUEST, "Invalid request data"),
}


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.

    1. Delegates to DRF's default handler for APIException subclasses.
    2. Maps known Python exceptions to appropriate HTTP responses.
    3. Logs and returns a generic 500 for anything else.
    """
    response = exception_handler(exc, context)

    if response is not None:
        return response

    for exc_type, (http_status, message) in EXCEPTION_MAP.items():
        if isinstance(exc, exc_type):
            return Response(data={"error": message}, status=http_status)

    view = context.get("view")
    view_name = view.__class__.__name__ if view else "unknown"
    logger.error(
        "op=exception_handler view=%s exception=%s",
        view_name,
        exc,
        exc_info=True,
    )
    return Response(
        data={"error": "An unknown error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
