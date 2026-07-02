from django.contrib import admin
from django.test import TestCase

from library_app.models import Book, BookIssue, User


class AdminRegistrationTests(TestCase):
    def test_models_are_registered(self):
        self.assertIn(User, admin.site._registry)
        self.assertIn(Book, admin.site._registry)
        self.assertIn(BookIssue, admin.site._registry)

    def test_user_admin_excludes_password_field(self):
        user_admin = admin.site._registry[User]
        self.assertIn("password", user_admin.exclude)
