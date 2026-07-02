import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from library_app.jwt_utils import generate_token
from library_app.models import BookIssue, User

from .factories import make_book, make_user


class BookIssueViewTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="issuer1")
        self.other_user = make_user(username="issuer2")
        self.book = make_book(total_copies=2, available_copies=2)

    def auth(self, user):
        token = generate_token(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_anonymous_cannot_issue(self):
        response = self.client.post("/api/issues/", {"book": self.book.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_issue_book_decrements_available_copies(self):
        response = self.client.post(
            "/api/issues/", {"book": self.book.id}, format="json", **self.auth(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

    def test_issue_unavailable_book_fails(self):
        self.book.available_copies = 0
        self.book.save(update_fields=["available_copies"])
        response = self.client.post(
            "/api/issues/", {"book": self.book.id}, format="json", **self.auth(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_exceed_max_books_allowed(self):
        for i in range(User.MAX_BOOKS_ALLOWED):
            b = make_book(title=f"Book {i}", isbn=f"888888888888{i}", total_copies=1)
            BookIssue.objects.create(user=self.user, book=b)

        response = self.client.post(
            "/api/issues/", {"book": self.book.id}, format="json", **self.auth(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_only_returns_own_issues(self):
        BookIssue.objects.create(user=self.user, book=self.book)
        BookIssue.objects.create(user=self.other_user, book=self.book)

        response = self.client.get("/api/issues/", **self.auth(self.user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class BookReturnViewTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="returner1")
        self.other_user = make_user(username="returner2")
        self.book = make_book(total_copies=1, available_copies=0)
        self.issue = BookIssue.objects.create(user=self.user, book=self.book)

    def auth(self, user):
        token = generate_token(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_return_own_book_on_time(self):
        response = self.client.post(f"/api/issues/{self.issue.id}/return/", **self.auth(self.user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fine_amount"], 0)
        self.assertIn("No fine", response.data["message"])
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

    def test_return_overdue_book_includes_fine(self):
        self.issue.due_date = datetime.date.today() - datetime.timedelta(days=3)
        self.issue.save(update_fields=["due_date"])

        response = self.client.post(f"/api/issues/{self.issue.id}/return/", **self.auth(self.user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fine_amount"], 15)
        self.assertIn("fine", response.data["message"].lower())

    def test_cannot_return_twice(self):
        self.client.post(f"/api/issues/{self.issue.id}/return/", **self.auth(self.user))
        response = self.client.post(f"/api/issues/{self.issue.id}/return/", **self.auth(self.user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_return_someone_elses_issue(self):
        response = self.client.post(
            f"/api/issues/{self.issue.id}/return/", **self.auth(self.other_user)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_nonexistent_issue(self):
        response = self.client.post("/api/issues/999999/return/", **self.auth(self.user))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
