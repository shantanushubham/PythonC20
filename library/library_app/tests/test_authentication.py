from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from library_app.authentication import JWTAuthentication
from library_app.jwt_utils import generate_token

from .factories import make_user

factory = APIRequestFactory()


class JWTAuthenticationTests(TestCase):
    def setUp(self):
        self.auth = JWTAuthentication()
        self.user = make_user(username="auth_user")
        self.token = generate_token(self.user)

    def test_no_header_returns_none(self):
        request = factory.get("/")
        self.assertIsNone(self.auth.authenticate(request))

    def test_valid_bearer_token_returns_user(self):
        request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        user, token = self.auth.authenticate(request)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(token, self.token)

    def test_wrong_keyword_returns_none(self):
        request = factory.get("/", HTTP_AUTHORIZATION=f"Token {self.token}")
        self.assertIsNone(self.auth.authenticate(request))

    def test_malformed_header_returns_none(self):
        request = factory.get("/", HTTP_AUTHORIZATION="Bearer")
        self.assertIsNone(self.auth.authenticate(request))

    def test_invalid_token_raises_authentication_failed(self):
        request = factory.get("/", HTTP_AUTHORIZATION="Bearer garbage.token.value")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_token_for_nonexistent_user_raises_authentication_failed(self):
        self.user.delete()
        request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_inactive_user_raises_authentication_failed(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_header(self):
        self.assertEqual(self.auth.authenticate_header(None), "Bearer")
