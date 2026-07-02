from rest_framework import status
from rest_framework.test import APITestCase

from library_app.jwt_utils import decode_token
from library_app.models import User

from .factories import DEFAULT_PASSWORD, make_user


class SignUpViewTests(APITestCase):
    def test_signup_creates_user_with_student_role(self):
        response = self.client.post(
            "/api/signup/",
            {"username": "newuser", "email": "n@example.com", "password": "Str0ngPassw0rd!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["role"], User.Role.STUDENT)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_duplicate_username_rejected(self):
        make_user(username="taken")
        response = self.client.post(
            "/api/signup/", {"username": "taken", "password": "Str0ngPassw0rd!"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_short_password_rejected(self):
        response = self.client.post(
            "/api/signup/", {"username": "shortpw", "password": "short"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="loginviewuser")

    def test_login_returns_valid_jwt(self):
        response = self.client.post(
            "/api/login/", {"username": "loginviewuser", "password": DEFAULT_PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        payload = decode_token(response.data["token"])
        self.assertEqual(payload["user_id"], self.user.id)

    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/login/", {"username": "loginviewuser", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="meviewuser")

    def test_me_requires_authentication(self):
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        login_resp = self.client.post(
            "/api/login/", {"username": "meviewuser", "password": DEFAULT_PASSWORD}, format="json"
        )
        token = login_resp.data["token"]
        response = self.client.get("/api/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "meviewuser")
