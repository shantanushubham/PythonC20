from rest_framework import status
from rest_framework.test import APITestCase

from library_app.jwt_utils import generate_token
from library_app.models import Book

from .factories import make_book, make_librarian, make_user


class BookViewSetTests(APITestCase):
    def setUp(self):
        self.student = make_user(username="student1")
        self.librarian = make_librarian(username="librarian1")
        self.book = make_book()

    def auth(self, user):
        token = generate_token(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_anonymous_cannot_list_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_can_list_books(self):
        response = self.client.get("/api/books/", **self.auth(self.student))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_can_retrieve_book(self):
        response = self.client.get(f"/api/books/{self.book.id}/", **self.auth(self.student))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["isbn"], self.book.isbn)

    def test_student_cannot_create_book(self):
        response = self.client.post(
            "/api/books/",
            {"title": "New", "author": "Someone", "isbn": "1111111111199", "total_copies": 1},
            format="json",
            **self.auth(self.student),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_book(self):
        response = self.client.post(
            "/api/books/",
            {"title": "New", "author": "Someone", "isbn": "1111111111199", "total_copies": 3},
            format="json",
            **self.auth(self.librarian),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["available_copies"], 3)

    def test_student_cannot_update_book(self):
        response = self.client.patch(
            f"/api/books/{self.book.id}/", {"total_copies": 9}, format="json", **self.auth(self.student)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_update_book(self):
        response = self.client.patch(
            f"/api/books/{self.book.id}/", {"total_copies": 9}, format="json", **self.auth(self.librarian)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["available_copies"], 9)

    def test_student_cannot_delete_book(self):
        response = self.client.delete(f"/api/books/{self.book.id}/", **self.auth(self.student))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_delete_book(self):
        response = self.client.delete(f"/api/books/{self.book.id}/", **self.auth(self.librarian))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.id).exists())
