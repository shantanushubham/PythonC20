import datetime

import bcrypt
from django.db import models


class User(models.Model):
    """Plain (non-Django-auth) user model. Signup/login are handled manually in
    this app's serializers/views rather than via django.contrib.auth."""

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        LIBRARIAN = "librarian", "Librarian"

    MAX_BOOKS_ALLOWED = 5
    BCRYPT_ROUNDS = 12

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_librarian(self):
        return self.role == self.Role.LIBRARIAN

    def set_password(self, raw_password):
        salt = bcrypt.gensalt(rounds=self.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
        self.password = hashed.decode("utf-8")

    def check_password(self, raw_password):
        if not self.password:
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password.encode("utf-8"))

    @property
    def is_authenticated(self):
        """Lets DRF's IsAuthenticated permission work with this plain model,
        the same way it would with django.contrib.auth's AbstractBaseUser."""
        return True

    @property
    def is_anonymous(self):
        return False


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(available_copies__lte=models.F("total_copies")),
                name="available_copies_lte_total_copies",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.available_copies}/{self.total_copies} available)"

    @property
    def is_available(self):
        return self.available_copies > 0


class BookIssue(models.Model):
    ISSUE_DURATION_DAYS = 15
    FINE_PER_DAY = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_issues")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "returned" if self.return_date else "issued"
        return f"{self.book.title} -> {self.user.username} ({status})"

    def save(self, *args, **kwargs):
        if not self.due_date:
            issue_date = self.issue_date or datetime.date.today()
            self.due_date = issue_date + datetime.timedelta(days=self.ISSUE_DURATION_DAYS)
        super().save(*args, **kwargs)

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def is_overdue(self):
        end_date = self.return_date or datetime.date.today()
        return end_date > self.due_date

    @property
    def fine_amount(self):
        end_date = self.return_date or datetime.date.today()
        overdue_days = (end_date - self.due_date).days
        return max(overdue_days, 0) * self.FINE_PER_DAY
