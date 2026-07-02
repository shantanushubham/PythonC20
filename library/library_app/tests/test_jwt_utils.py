import datetime

import jwt
from django.conf import settings
from django.test import TestCase

from library_app.jwt_utils import TokenError, decode_token, generate_token

from .factories import make_user


class JWTUtilsTests(TestCase):
    def setUp(self):
        self.user = make_user(username="jwt_user")

    def test_generate_token_returns_a_string(self):
        token = generate_token(self.user)
        self.assertIsInstance(token, str)

    def test_decode_token_roundtrip(self):
        token = generate_token(self.user)
        payload = decode_token(token)
        self.assertEqual(payload["user_id"], self.user.id)
        self.assertEqual(payload["username"], self.user.username)

    def test_decode_token_rejects_garbage(self):
        with self.assertRaises(TokenError):
            decode_token("not-a-real-token")

    def test_decode_token_rejects_expired_token(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "user_id": self.user.id,
            "username": self.user.username,
            "iat": now - datetime.timedelta(hours=2),
            "exp": now - datetime.timedelta(hours=1),
        }
        expired_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        with self.assertRaises(TokenError):
            decode_token(expired_token)

    def test_decode_token_rejects_wrong_signing_key(self):
        payload = {"user_id": self.user.id, "username": self.user.username}
        token = jwt.encode(payload, "a-different-secret", algorithm=settings.JWT_ALGORITHM)
        with self.assertRaises(TokenError):
            decode_token(token)
