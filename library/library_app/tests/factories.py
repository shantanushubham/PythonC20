import datetime

from library_app.models import Book, BookIssue, User

DEFAULT_PASSWORD = "Str0ngPassw0rd!"


def make_user(username="testuser", role=User.Role.STUDENT, password=DEFAULT_PASSWORD, **kwargs):
    user = User(username=username, role=role, **kwargs)
    user.set_password(password)
    user.save()
    return user


def make_librarian(username="librarian", password=DEFAULT_PASSWORD, **kwargs):
    return make_user(username=username, role=User.Role.LIBRARIAN, password=password, **kwargs)


def make_book(title="Dune", author="Frank Herbert", isbn="9780441172719", total_copies=1, **kwargs):
    return Book.objects.create(
        title=title,
        author=author,
        isbn=isbn,
        total_copies=total_copies,
        available_copies=kwargs.pop("available_copies", total_copies),
        **kwargs,
    )


def make_issue(user, book, issue_date=None, return_date=None):
    """Creates a BookIssue with a backdated `issue_date`/`due_date`.

    `issue_date` is `auto_now_add=True`, so a normal `.save()` always
    overwrites it with today -- QuerySet.update() bypasses that."""
    issue = BookIssue.objects.create(user=user, book=book)
    if issue_date is not None:
        BookIssue.objects.filter(pk=issue.pk).update(
            issue_date=issue_date,
            due_date=issue_date + datetime.timedelta(days=BookIssue.ISSUE_DURATION_DAYS),
            return_date=return_date,
        )
        issue.refresh_from_db()
    return issue
