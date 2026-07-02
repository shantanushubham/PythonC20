from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from library_app.permissions import IsLibrarianOrReadOnly

from .factories import make_librarian, make_user

factory = APIRequestFactory()


class IsLibrarianOrReadOnlyTests(TestCase):
    def setUp(self):
        self.permission = IsLibrarianOrReadOnly()
        self.student = make_user()
        self.librarian = make_librarian()

    def _request(self, method):
        request = getattr(factory, method.lower())("/")
        return request

    def test_anonymous_denied_even_for_safe_methods(self):
        request = self._request("get")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))

    def test_student_can_read(self):
        request = self._request("get")
        request.user = self.student
        self.assertTrue(self.permission.has_permission(request, None))

    def test_student_cannot_write(self):
        request = self._request("post")
        request.user = self.student
        self.assertFalse(self.permission.has_permission(request, None))

    def test_librarian_can_read(self):
        request = self._request("get")
        request.user = self.librarian
        self.assertTrue(self.permission.has_permission(request, None))

    def test_librarian_can_write(self):
        for method in ("post", "put", "patch", "delete"):
            request = self._request(method)
            request.user = self.librarian
            self.assertTrue(self.permission.has_permission(request, None), msg=method)
