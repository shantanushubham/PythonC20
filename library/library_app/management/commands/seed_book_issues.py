import datetime
import random

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from library_app.models import Book, BookIssue, User

RANGE_START = datetime.date(2025, 1, 1)
RETURN_PROBABILITY = 0.75


def _aware_midnight(date):
    return timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))


class Command(BaseCommand):
    help = (
        "Populates BookIssue with randomized historical rows (issue_date spread "
        "across 2025-2026) for demo/testing purposes. auto_now_add fields "
        "(issue_date, created_at) are backdated via QuerySet.update(), which "
        "bypasses the auto-now behaviour that a normal .save() would enforce."
    )

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100, help="Number of BookIssue rows to create.")
        parser.add_argument(
            "--clear", action="store_true", help="Delete existing BookIssue rows before seeding."
        )

    def handle(self, *args, **options):
        count = options["count"]

        if not User.objects.exists():
            self.stdout.write("No users found -- running seed_users first.")
            call_command("seed_users")
        if not Book.objects.exists():
            self.stdout.write("No books found -- running seed_books first.")
            call_command("seed_books")

        users = list(User.objects.all())
        books = list(Book.objects.all())

        if options["clear"]:
            deleted, _ = BookIssue.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing BookIssue row(s).")
            for book in books:
                book.available_copies = book.total_copies
            Book.objects.bulk_update(books, ["available_copies"])

        today = datetime.date.today()
        total_days = (today - RANGE_START).days

        # Respect currently-active issues (return_date is null) so we never
        # push a book's active count above its total_copies.
        active_counts = {book.id: book.total_copies - book.available_copies for book in books}

        created = 0
        with transaction.atomic():
            for _ in range(count):
                issue_date = RANGE_START + datetime.timedelta(days=random.randint(0, total_days))
                due_date = issue_date + datetime.timedelta(days=BookIssue.ISSUE_DURATION_DAYS)

                book = random.choice(books)
                user = random.choice(users)

                will_return = random.random() < RETURN_PROBABILITY
                if not will_return and active_counts[book.id] >= book.total_copies:
                    # No room to leave this one active -- return it instead.
                    will_return = True

                return_date = None
                if will_return:
                    days_held = random.randint(1, 45)
                    return_date = min(issue_date + datetime.timedelta(days=days_held), today)
                    if return_date <= issue_date:
                        return_date = issue_date + datetime.timedelta(days=1)
                else:
                    active_counts[book.id] += 1

                issue = BookIssue.objects.create(user=user, book=book)
                BookIssue.objects.filter(pk=issue.pk).update(
                    issue_date=issue_date,
                    due_date=due_date,
                    return_date=return_date,
                    created_at=_aware_midnight(issue_date),
                    updated_at=_aware_midnight(return_date or issue_date),
                )
                created += 1

            for book in books:
                book.available_copies = book.total_copies - active_counts[book.id]
            Book.objects.bulk_update(books, ["available_copies"])

        self.stdout.write(self.style.SUCCESS(f"Created {created} BookIssue row(s) spanning 2025-2026."))
