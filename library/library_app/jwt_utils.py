import datetime

import jwt
from django.conf import settings


class TokenError(Exception):
    """Raised for any invalid/expired/malformed token."""


def generate_token(user):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user_id": user.id,
        "username": user.username,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token.") from exc
