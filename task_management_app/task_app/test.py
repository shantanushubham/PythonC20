import uuid
from datetime import date, timedelta, datetime, timezone
from unittest.mock import MagicMock, patch

from django.test import TestCase, RequestFactory
from rest_framework.test import APITestCase, APIClient
from rest_framework.exceptions import AuthenticationFailed

from task_app.models import Task, User
from task_app.utils import BCruptUtil, JWTUtil
from task_app.authentication import JWTAuthentication
from task_app.serialisers import LoginSerialiser, SignUpSerialiser, TaskSerialiser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(**kwargs):
    """Create a User with sensible test defaults."""
    defaults = {
        "first_name": "Test",
        "last_name": "User",
        "dob": date(1990, 1, 1),
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "password": BCruptUtil.encrypt_password("password123"),
    }
    defaults.update(kwargs)
    return User.objects.create(**defaults)


def make_task(owner, **kwargs):
    """Create a Task with sensible test defaults."""
    defaults = {
        "owner": owner,
        "title": "Test Task",
        "description": "Test description",
        "due_at": date.today() + timedelta(days=7),
    }
    defaults.update(kwargs)
    return Task.objects.create(**defaults)


# ===========================================================================
# Utils
# ===========================================================================

class BCruptUtilTests(TestCase):

    def test_encrypt_password_returns_different_string(self):
        hashed = BCruptUtil.encrypt_password("secret")
        self.assertNotEqual("secret", hashed)

    def test_verify_correct_password_returns_true(self):
        hashed = BCruptUtil.encrypt_password("mypassword")
        self.assertTrue(BCruptUtil.verify_password("mypassword", hashed))

    def test_verify_wrong_password_returns_false(self):
        hashed = BCruptUtil.encrypt_password("mypassword")
        self.assertFalse(BCruptUtil.verify_password("wrongpassword", hashed))


class JWTUtilTests(TestCase):

    def test_create_token_returns_string(self):
        token = JWTUtil.create_token(uuid.uuid4())
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_verify_valid_token(self):
        user_id = uuid.uuid4()
        token = JWTUtil.create_token(user_id)
        result = JWTUtil.verify_token(token)
        self.assertTrue(result["valid"])
        self.assertEqual(result["user_id"], str(user_id))

    def test_verify_expired_token_returns_invalid(self):
        import jwt as pyjwt
        expired_payload = {
            "user_id": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "iat": datetime.now(timezone.utc) - timedelta(minutes=2),
        }
        token = pyjwt.encode(expired_payload, JWTUtil.SECRET_KEY, algorithm=JWTUtil.ALGORITHM)
        result = JWTUtil.verify_token(token)
        self.assertFalse(result["valid"])
        self.assertIn("expired", result["error"].lower())

    def test_verify_invalid_token_returns_invalid(self):
        result = JWTUtil.verify_token("not.a.valid.token")
        self.assertFalse(result["valid"])
        self.assertIn("invalid", result["error"].lower())

    def test_create_token_accepts_string_id(self):
        token = JWTUtil.create_token("some-string-id")
        result = JWTUtil.verify_token(token)
        self.assertTrue(result["valid"])
        self.assertEqual(result["user_id"], "some-string-id")


# ===========================================================================
# Models
# ===========================================================================

class UserModelTests(TestCase):

    def test_create_adult_user_succeeds(self):
        user = make_user()
        self.assertIsNotNone(user.pk)

    def test_create_underage_user_raises(self):
        young_dob = date.today() - timedelta(days=365 * 16)
        with self.assertRaises(ValueError):
            make_user(dob=young_dob)

    def test_create_user_exactly_18_today_succeeds(self):
        today = date.today()
        dob_18 = date(today.year - 18, today.month, today.day)
        user = make_user(dob=dob_18)
        self.assertIsNotNone(user.pk)

    def test_create_user_whose_18th_birthday_is_tomorrow_raises(self):
        tomorrow = date.today() + timedelta(days=1)
        dob_17 = date(tomorrow.year - 18, tomorrow.month, tomorrow.day)
        with self.assertRaises(ValueError):
            make_user(dob=dob_17)

    def test_user_str_returns_full_name(self):
        user = make_user(first_name="Jane", last_name="Doe")
        self.assertEqual(str(user), "Jane Doe")


class TaskModelTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_create_task_with_future_due_date_succeeds(self):
        task = make_task(self.user)
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.status, Task.Status.PENDING)

    def test_task_default_status_is_pending(self):
        task = make_task(self.user)
        self.assertEqual(task.status, Task.Status.PENDING)

    def test_update_task_due_at_same_as_created_at_raises(self):
        task = make_task(self.user)
        # Refresh from DB so created_at is populated
        task.refresh_from_db()
        task.due_at = task.created_at  # same day → invalid
        with self.assertRaises(ValueError):
            task.save()

    def test_update_task_due_at_before_created_at_raises(self):
        task = make_task(self.user)
        task.refresh_from_db()
        task.due_at = task.created_at - timedelta(days=1)
        with self.assertRaises(ValueError):
            task.save()

    def test_task_str_contains_title_and_owner(self):
        task = make_task(self.user, title="My Task")
        self.assertIn("My Task", str(task))
        self.assertIn(str(self.user), str(task))

    def test_task_status_choices(self):
        self.assertIn("PENDING", Task.Status.values)
        self.assertIn("IN_PROGRESS", Task.Status.values)
        self.assertIn("DONE", Task.Status.values)


# ===========================================================================
# Serialisers
# ===========================================================================

class TaskSerialiserValidationTests(TestCase):

    def test_validate_due_at_future_date_is_valid(self):
        serialiser = TaskSerialiser()
        future = date.today() + timedelta(days=5)
        self.assertEqual(serialiser.validate_due_at(future), future)

    def test_validate_due_at_today_raises(self):
        from rest_framework import serializers
        serialiser = TaskSerialiser()
        with self.assertRaises(serializers.ValidationError):
            serialiser.validate_due_at(date.today())

    def test_validate_due_at_past_date_raises(self):
        from rest_framework import serializers
        serialiser = TaskSerialiser()
        with self.assertRaises(serializers.ValidationError):
            serialiser.validate_due_at(date.today() - timedelta(days=1))


class LoginSerialiserTests(TestCase):

    def setUp(self):
        self.plain_password = "testpass123"
        self.user = make_user(
            username="logintest",
            password=BCruptUtil.encrypt_password(self.plain_password),
        )

    def test_valid_credentials_returns_user(self):
        serialiser = LoginSerialiser(data={"username": "logintest", "password": self.plain_password})
        self.assertTrue(serialiser.is_valid(), serialiser.errors)
        self.assertEqual(serialiser.validated_data["user"], self.user)

    def test_wrong_password_is_invalid(self):
        serialiser = LoginSerialiser(data={"username": "logintest", "password": "wrongpass"})
        self.assertFalse(serialiser.is_valid())

    def test_nonexistent_username_is_invalid(self):
        serialiser = LoginSerialiser(data={"username": "nobody", "password": "anything"})
        self.assertFalse(serialiser.is_valid())


class SignUpSerialiserTests(TestCase):

    def test_create_hashes_password(self):
        data = {
            "first_name": "New",
            "last_name": "Person",
            "dob": "1995-06-15",
            "username": "newperson",
            "password": "plainpassword",
        }
        serialiser = SignUpSerialiser(data=data)
        self.assertTrue(serialiser.is_valid(), serialiser.errors)
        user = serialiser.save()
        self.assertNotEqual(user.password, "plainpassword")
        self.assertTrue(BCruptUtil.verify_password("plainpassword", user.password))


# ===========================================================================
# Authentication
# ===========================================================================

class JWTAuthenticationTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.auth = JWTAuthentication()
        self.factory = RequestFactory()

    def _make_request(self, auth_header=None):
        request = self.factory.get("/")
        if auth_header:
            request.META["HTTP_AUTHORIZATION"] = auth_header
        return request

    def test_missing_authorization_header_returns_none(self):
        request = self._make_request()
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_non_bearer_scheme_raises(self):
        request = self._make_request("Basic sometoken")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_valid_token_returns_user_and_token(self):
        token = JWTUtil.create_token(self.user.id)
        request = self._make_request(f"Bearer {token}")
        user, returned_token = self.auth.authenticate(request)
        self.assertEqual(user, self.user)
        self.assertEqual(returned_token, token)

    def test_expired_token_raises(self):
        import jwt as pyjwt
        expired_payload = {
            "user_id": str(self.user.id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "iat": datetime.now(timezone.utc) - timedelta(minutes=2),
        }
        token = pyjwt.encode(expired_payload, JWTUtil.SECRET_KEY, algorithm=JWTUtil.ALGORITHM)
        request = self._make_request(f"Bearer {token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_invalid_token_raises(self):
        request = self._make_request("Bearer thisisnotavalidtoken")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_token_with_nonexistent_user_raises(self):
        phantom_id = uuid.uuid4()
        token = JWTUtil.create_token(phantom_id)
        request = self._make_request(f"Bearer {token}")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)


# ===========================================================================
# Views
# ===========================================================================

class LoginViewTests(APITestCase):

    def setUp(self):
        self.plain_password = "viewpass123"
        self.user = make_user(
            username="viewlogin",
            password=BCruptUtil.encrypt_password(self.plain_password),
        )
        self.url = "/api/auth/login/"

    def test_login_success_returns_token_and_user(self):
        response = self.client.post(self.url, {"username": "viewlogin", "password": self.plain_password})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "viewlogin")

    def test_login_wrong_password_returns_400(self):
        response = self.client.post(self.url, {"username": "viewlogin", "password": "wrongpass"})
        self.assertEqual(response.status_code, 400)

    def test_login_nonexistent_user_returns_400(self):
        response = self.client.post(self.url, {"username": "ghost", "password": "anything"})
        self.assertEqual(response.status_code, 400)

    def test_login_missing_fields_returns_400(self):
        response = self.client.post(self.url, {"username": "viewlogin"})
        self.assertEqual(response.status_code, 400)


class SignUpViewTests(APITestCase):

    url = "/api/auth/signup/"

    def _valid_payload(self, **overrides):
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "dob": "1998-03-20",
            "username": f"alice_{uuid.uuid4().hex[:6]}",
            "password": "securepass",
        }
        data.update(overrides)
        return data

    def test_signup_success_returns_201_with_token(self):
        response = self.client.post(self.url, self._valid_payload())
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_signup_duplicate_username_returns_400(self):
        payload = self._valid_payload(username="dupuser")
        make_user(username="dupuser")
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 400)

    def test_signup_underage_returns_400(self):
        young_dob = (date.today() - timedelta(days=365 * 16)).isoformat()
        response = self.client.post(self.url, self._valid_payload(dob=young_dob))
        self.assertEqual(response.status_code, 400)

    def test_signup_missing_required_field_returns_400(self):
        payload = self._valid_payload()
        del payload["username"]
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 400)


class TaskViewSetTests(APITestCase):

    def setUp(self):
        self.user = make_user(username="taskowner")
        self.token = JWTUtil.create_token(self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.task = make_task(self.user, title="Initial Task")

    def test_list_tasks_returns_200(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)

    def test_list_tasks_returns_existing_task(self):
        response = self.client.get("/tasks/")
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Initial Task", titles)

    def test_list_tasks_filter_by_valid_status(self):
        response = self.client.get("/tasks/?status=PENDING")
        self.assertEqual(response.status_code, 200)

    def test_list_tasks_filter_by_invalid_status_returns_400(self):
        response = self.client.get("/tasks/?status=INVALID")
        self.assertEqual(response.status_code, 400)

    def test_list_tasks_status_filter_is_case_insensitive(self):
        response = self.client.get("/tasks/?status=pending")
        self.assertEqual(response.status_code, 200)

    def test_create_task_returns_201(self):
        payload = {
            "title": "New Task",
            "description": "Doing something",
            "due_at": (date.today() + timedelta(days=10)).isoformat(),
        }
        response = self.client.post("/tasks/", payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Task")

    def test_create_task_sets_authenticated_user_as_owner(self):
        payload = {
            "title": "Owner Task",
            "description": "Check owner",
            "due_at": (date.today() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post("/tasks/", payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["owner"]["id"], str(self.user.id))

    def test_create_task_due_date_today_returns_400(self):
        payload = {
            "title": "Bad Task",
            "description": "Due today",
            "due_at": date.today().isoformat(),
        }
        response = self.client.post("/tasks/", payload)
        self.assertEqual(response.status_code, 400)

    def test_retrieve_task_returns_200(self):
        response = self.client.get(f"/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Initial Task")

    def test_retrieve_nonexistent_task_returns_404(self):
        response = self.client.get(f"/tasks/{uuid.uuid4()}/")
        self.assertEqual(response.status_code, 404)

    def test_update_task_title(self):
        payload = {
            "title": "Updated Title",
            "description": self.task.description,
            "due_at": self.task.due_at.isoformat(),
        }
        response = self.client.put(f"/tasks/{self.task.id}/", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_delete_task_returns_204(self):
        task = make_task(self.user, title="To Delete")
        response = self.client.delete(f"/tasks/{task.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_mark_complete_changes_status_to_done(self):
        response = self.client.post(f"/tasks/{self.task.id}/mark_complete/")
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.DONE)

    def test_mark_complete_already_done_returns_200_with_message(self):
        self.task.status = Task.Status.DONE
        self.task.save()
        response = self.client.post(f"/tasks/{self.task.id}/mark_complete/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("already", response.data["message"])

    def test_mark_complete_nonexistent_task_returns_404(self):
        response = self.client.post(f"/tasks/{uuid.uuid4()}/mark_complete/")
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_create_is_rejected(self):
        self.client.credentials()  # clear auth
        payload = {
            "title": "Anon Task",
            "description": "Should fail",
            "due_at": (date.today() + timedelta(days=5)).isoformat(),
        }
        response = self.client.post("/tasks/", payload)
        # Without auth, request.user is AnonymousUser which cannot be stored
        # as a FK — the server should reject this with a 4xx or 5xx response.
        self.assertGreaterEqual(response.status_code, 400)

    def test_in_progress_endpoint_returns_200(self):
        response = self.client.get("/tasks/in_progress/")
        self.assertEqual(response.status_code, 200)

    def test_in_progress_endpoint_returns_matching_tasks(self):
        ananya = make_user(first_name="Ananya", last_name="Gupta", username="ananya")
        make_task(ananya, title="Ananya's Task", status=Task.Status.IN_PROGRESS)
        response = self.client.get("/tasks/in_progress/")
        self.assertEqual(response.status_code, 200)
        titles = [row["title"] for row in response.data]
        self.assertIn("Ananya's Task", titles)
