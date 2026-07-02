from django.core.management.base import BaseCommand

from library_app.models import Book

SEED_BOOKS = [
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "9780441172719",
        "total_copies": 3,
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "9780547928227",
        "total_copies": 2,
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "9780451524935",
        "total_copies": 4,
    },
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "total_copies": 2,
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas & Andrew Hunt",
        "isbn": "9780135957059",
        "total_copies": 1,
    },
]


class Command(BaseCommand):
    help = "Seeds a handful of demo books (idempotent: skips books that already exist by ISBN)."

    def handle(self, *args, **options):
        created_count = 0
        for data in SEED_BOOKS:
            if Book.objects.filter(isbn=data["isbn"]).exists():
                self.stdout.write(f"Skipping '{data['title']}' (already exists).")
                continue

            book = Book.objects.create(
                title=data["title"],
                author=data["author"],
                isbn=data["isbn"],
                total_copies=data["total_copies"],
                available_copies=data["total_copies"],
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"Created book '{book.title}' ({book.total_copies} copies).")
            )

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} book(s) created."))
