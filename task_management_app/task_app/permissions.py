import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class TestPermission(BasePermission):

  message = "You must be an admin."

  def has_permission(self, request, view):
    allowed = request.user and str(request.user.type) is not None
    logger.info(
        "op=has_permission user_id=%s view=%s allowed=%s",
        getattr(request.user, "id", None),
        view.__class__.__name__,
        allowed,
    )
    return allowed


#  /add_numbers?a=5&b=10

# Response is {"sum": 15}
# What if the response is {"success": true, "result": 15}
