import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase

from library_app.models import Book, BookIssue, User

from .factories import make_book, make_librarian, make_user


class UserModelTests(TestCase):
    def test_set_password_hashes_with_bcrypt_12_rounds(self):
        user = make_user()
        self.assertTrue(user.password.startswith("$2b$12$"))
        self.assertNotEqual(user.password, "Str0ngPassw0rd!")

    def test_check_password_correct_and_incorrect(self):
        user = make_user(password="correct-horse-battery")
        self.assertTrue(user.check_password("correct-horse-battery"))
        self.assertFalse(user.check_password("wrong-password"))

    def test_check_password_with_no_password_set_returns_false(self):
        user = User(username="nopass")
        self.assertFalse(user.check_password("anything"))

    def test_default_role_is_student(self):
        user = make_user()
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertFalse(user.is_librarian)

    def test_librarian_role(self):
        librarian = make_librarian()
        self.assertTrue(librarian.is_librarian)

    def test_is_authenticated_and_is_anonymous(self):
        user = make_user()
        self.assertTrue(user.is_authenticated)
        self.assertFalse(user.is_anonymous)

    def test_username_must_be_unique(self):
        make_user(username="dupe")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_user(username="dupe")


class BookModelTests(TestCase):
    def test_is_available_true_when_copies_remain(self):
        book = make_book(total_copies=2, available_copies=1)
        self.assertTrue(book.is_available)

    def test_is_available_false_when_no_copies_remain(self):
        book = make_book(total_copies=2, available_copies=0)
        self.assertFalse(book.is_available)

    def test_isbn_must_be_unique(self):
        make_book(isbn="1111111111111")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_book(isbn="1111111111111")

    def test_available_copies_cannot_exceed_total_copies(self):
        book = Book(title="X", author="Y", isbn="2222222222222", total_copies=1, available_copies=2)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                book.save()


class BookIssueModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.book = make_book()

    def test_due_date_defaults_to_15_days_after_issue(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        self.assertEqual(issue.due_date, issue.issue_date + datetime.timedelta(days=15))

    def test_explicit_due_date_is_not_overwritten(self):
        custom_due = datetime.date.today() + datetime.timedelta(days=1)
        issue = BookIssue(user=self.user, book=self.book, due_date=custom_due)
        issue.save()
        self.assertEqual(issue.due_date, custom_due)

    def test_is_returned(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        self.assertFalse(issue.is_returned)
        issue.return_date = datetime.date.today()
        self.assertTrue(issue.is_returned)

    def test_is_overdue_false_when_within_due_date(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        self.assertFalse(issue.is_overdue)

    def test_is_overdue_true_when_past_due_date_and_not_returned(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        issue.due_date = datetime.date.today() - datetime.timedelta(days=1)
        issue.save(update_fields=["due_date"])
        self.assertTrue(issue.is_overdue)

    def test_fine_amount_zero_when_on_time(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        self.assertEqual(issue.fine_amount, 0)

    def test_fine_amount_charges_5_rs_per_overdue_day(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        issue.due_date = datetime.date.today() - datetime.timedelta(days=3)
        issue.return_date = datetime.date.today()
        self.assertEqual(issue.fine_amount, 15)

    def test_fine_amount_uses_today_when_not_yet_returned(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        issue.due_date = datetime.date.today() - datetime.timedelta(days=2)
        issue.save(update_fields=["due_date"])
        self.assertEqual(issue.fine_amount, 10)

    def test_str_representation(self):
        issue = BookIssue.objects.create(user=self.user, book=self.book)
        self.assertIn("issued", str(issue))
        issue.return_date = datetime.date.today()
        self.assertIn("returned", str(issue))
