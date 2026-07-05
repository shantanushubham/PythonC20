import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import make_book, make_issue, make_user

TODAY = datetime.date.today()
RECENT = TODAY - datetime.timedelta(days=30)  # within the last 6 months
OLD = TODAY - datetime.timedelta(days=210)  # more than 6 months ago


class MostIssuedBookViewTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="reader1")
        self.other_user = make_user(username="reader2")

    def test_accessible_without_authentication(self):
        response = self.client.get("/api/most_issued/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_counts_issues_within_last_6_months(self):
        book = make_book(title="Recent Reads", isbn="1000000000001", total_copies=5)
        make_issue(self.user, book, issue_date=RECENT)
        make_issue(self.other_user, book, issue_date=RECENT)
        make_issue(self.user, book, issue_date=OLD)  # should be excluded

        response = self.client.get("/api/most_issued/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        entry = next(b for b in response.data if b["id"] == book.id)
        self.assertEqual(entry["issued_count"], 2)

    def test_each_book_appears_only_once(self):
        # Regression test for the annotate()/Count(filter=...) bug: a book
        # with both recent AND old issues must appear as a single row, not
        # split into multiple rows with partial counts.
        book = make_book(title="Mixed History", isbn="1000000000002", total_copies=5)
        make_issue(self.user, book, issue_date=RECENT)
        make_issue(self.other_user, book, issue_date=OLD)

        response = self.client.get("/api/most_issued/")
        matching = [b for b in response.data if b["id"] == book.id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["issued_count"], 1)

    def test_ordered_by_issued_count_descending(self):
        popular = make_book(title="Popular", isbn="1000000000003", total_copies=5)
        unpopular = make_book(title="Unpopular", isbn="1000000000004", total_copies=5)
        for _ in range(3):
            make_issue(self.user, popular, issue_date=RECENT)
        make_issue(self.user, unpopular, issue_date=RECENT)

        response = self.client.get("/api/most_issued/")
        ids_in_order = [b["id"] for b in response.data]
        self.assertLess(ids_in_order.index(popular.id), ids_in_order.index(unpopular.id))

    def test_returns_at_most_5_books(self):
        for i in range(7):
            book = make_book(title=f"Book {i}", isbn=f"200000000000{i}", total_copies=1)
            make_issue(self.user, book, issue_date=RECENT)

        response = self.client.get("/api/most_issued/")
        self.assertLessEqual(len(response.data), 5)

    def test_response_fields(self):
        book = make_book(title="Field Check", isbn="1000000000005", total_copies=5)
        make_issue(self.user, book, issue_date=RECENT)

        response = self.client.get("/api/most_issued/")
        entry = next(b for b in response.data if b["id"] == book.id)
        self.assertEqual(
            set(entry.keys()), {"id", "title", "author", "isbn", "issued_count"}
        )
        self.assertEqual(entry["title"], "Field Check")
        self.assertEqual(entry["isbn"], "1000000000005")

    def test_book_with_no_issues_can_still_appear_with_zero_count(self):
        make_book(title="Never Issued", isbn="1000000000006", total_copies=1)

        response = self.client.get("/api/most_issued/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry = next((b for b in response.data if b["isbn"] == "1000000000006"), None)
        if entry is not None:
            self.assertEqual(entry["issued_count"], 0)
