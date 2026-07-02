import datetime

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from library_app.models import Book, BookIssue, User
from library_app.serializers import (
    BookIssueSerializer,
    BookReturnSerializer,
    BookSerializer,
    LoginSerializer,
    UserSerializer,
)

from .factories import make_book, make_user

factory = APIRequestFactory()


def request_for(user):
    req = factory.get("/")
    req.user = user
    return req


class UserSerializerTests(TestCase):
    def test_create_hashes_password_and_defaults_role_to_student(self):
        serializer = UserSerializer(data={"username": "newbie", "password": "Str0ngPassw0rd!"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertNotEqual(user.password, "Str0ngPassw0rd!")
        self.assertTrue(user.check_password("Str0ngPassw0rd!"))
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_password_too_short_is_rejected(self):
        serializer = UserSerializer(data={"username": "newbie", "password": "short"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_is_write_only(self):
        user = make_user(username="hideme")
        data = UserSerializer(user).data
        self.assertNotIn("password", data)

    def test_role_is_read_only(self):
        serializer = UserSerializer(data={"username": "wannabe_admin", "password": "Str0ngPassw0rd!", "role": "librarian"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.role, User.Role.STUDENT)


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.user = make_user(username="loginuser", password="Str0ngPassw0rd!")

    def test_valid_credentials(self):
        serializer = LoginSerializer(data={"username": "loginuser", "password": "Str0ngPassw0rd!"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_password(self):
        serializer = LoginSerializer(data={"username": "loginuser", "password": "wrong"})
        self.assertFalse(serializer.is_valid())

    def test_nonexistent_username(self):
        serializer = LoginSerializer(data={"username": "ghost", "password": "whatever"})
        self.assertFalse(serializer.is_valid())

    def test_inactive_user_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        serializer = LoginSerializer(data={"username": "loginuser", "password": "Str0ngPassw0rd!"})
        self.assertFalse(serializer.is_valid())


class BookSerializerTests(TestCase):
    def test_create_sets_available_copies_equal_to_total(self):
        serializer = BookSerializer(data={"title": "T", "author": "A", "isbn": "1234567890123", "total_copies": 4})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.available_copies, 4)

    def test_total_copies_must_be_at_least_one(self):
        serializer = BookSerializer(data={"title": "T", "author": "A", "isbn": "1234567890124", "total_copies": 0})
        self.assertFalse(serializer.is_valid())

    def test_available_copies_is_read_only(self):
        serializer = BookSerializer(
            data={
                "title": "T",
                "author": "A",
                "isbn": "1234567890125",
                "total_copies": 3,
                "available_copies": 999,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.available_copies, 3)

    def test_update_increases_available_copies_by_delta(self):
        book = make_book(total_copies=2, available_copies=2)
        serializer = BookSerializer(book, data={"total_copies": 5}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.available_copies, 5)

    def test_update_rejects_reducing_below_issued_count(self):
        book = make_book(total_copies=5, available_copies=1)  # 4 issued out
        serializer = BookSerializer(book, data={"total_copies": 2}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()


class BookIssueSerializerTests(TestCase):
    def setUp(self):
        self.user = make_user(username="issuer")
        self.book = make_book(total_copies=2, available_copies=2)

    def test_create_decrements_available_copies(self):
        serializer = BookIssueSerializer(data={"book": self.book.id}, context={"request": request_for(self.user)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        issue = serializer.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        self.assertEqual(issue.user, self.user)
        self.assertEqual(issue.due_date, issue.issue_date + datetime.timedelta(days=15))

    def test_rejects_unavailable_book(self):
        self.book.available_copies = 0
        self.book.save(update_fields=["available_copies"])
        serializer = BookIssueSerializer(data={"book": self.book.id}, context={"request": request_for(self.user)})
        self.assertFalse(serializer.is_valid())

    def test_rejects_when_user_already_has_max_books(self):
        for i in range(User.MAX_BOOKS_ALLOWED):
            b = make_book(title=f"Book {i}", isbn=f"999999999999{i}", total_copies=1)
            BookIssue.objects.create(user=self.user, book=b)

        serializer = BookIssueSerializer(data={"book": self.book.id}, context={"request": request_for(self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class BookReturnSerializerTests(TestCase):
    def setUp(self):
        self.user = make_user(username="returner")
        self.book = make_book(total_copies=1, available_copies=0)
        self.issue = BookIssue.objects.create(user=self.user, book=self.book)

    def test_update_sets_return_date_and_increments_copies(self):
        serializer = BookReturnSerializer(self.issue, data={}, context={"request": request_for(self.user)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        issue = serializer.save()
        self.assertEqual(issue.return_date, datetime.date.today())
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

    def test_double_return_is_rejected(self):
        self.issue.return_date = datetime.date.today()
        self.issue.save(update_fields=["return_date"])
        serializer = BookReturnSerializer(self.issue, data={}, context={"request": request_for(self.user)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_fine_amount_reflects_overdue_days(self):
        self.issue.due_date = datetime.date.today() - datetime.timedelta(days=2)
        self.issue.save(update_fields=["due_date"])
        serializer = BookReturnSerializer(self.issue, data={}, context={"request": request_for(self.user)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        issue = serializer.save()
        self.assertEqual(issue.fine_amount, 10)
