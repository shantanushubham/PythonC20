import logging

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from task_app.models import User
from task_app.utils import JWTUtil

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        logger.info("op=authenticate path=%s", request.path)
        if not auth_header:
            logger.info("op=authenticate status=skipped reason=no_credentials path=%s", request.path)
            return None  # No credentials provided; skip to next authenticator

        if not auth_header.startswith("Bearer "):
            logger.warning("op=authenticate status=failed reason=invalid_scheme path=%s", request.path)
            raise AuthenticationFailed("Authorization header must use Bearer scheme.")

        token = auth_header[7:]
        result = JWTUtil.verify_token(token)

        if not result["valid"]:
            logger.warning("op=authenticate status=failed reason=%s path=%s", result["error"], request.path)
            raise AuthenticationFailed(result["error"])

        try:
            user = User.objects.get(id=result["user_id"])
        except User.DoesNotExist:
            logger.warning("op=authenticate status=failed reason=user_not_found user_id=%s", result["user_id"])
            raise AuthenticationFailed("User not found.")

        logger.info("op=authenticate status=success user_id=%s path=%s", user.id, request.path)
        return (user, token)  # Returning a tuple with a user and the token
