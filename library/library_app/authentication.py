from rest_framework import authentication, exceptions

from .jwt_utils import TokenError, decode_token
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """Manual JWT authentication: expects `Authorization: Bearer <token>`."""

    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        try:
            payload = decode_token(token)
        except TokenError as exc:
            raise exceptions.AuthenticationFailed(str(exc)) from exc

        try:
            user = User.objects.get(pk=payload["user_id"])
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found.") from exc

        if not user.is_active:
            raise exceptions.AuthenticationFailed("This account has been deactivated.")

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword