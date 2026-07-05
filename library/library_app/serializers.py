from dataclasses import field
import datetime

from django.db import transaction
from rest_framework import serializers

from .models import Book, BookIssue, User


class LoginSerializer(serializers.Serializer):
    """Manually verifies credentials against our own User model (no
    django.contrib.auth involved)."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs["username"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Used for signup and for exposing basic user info (e.g. nested in other serializers)."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "password"]
        read_only_fields = ["role"]

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "total_copies",
            "available_copies",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["available_copies", "created_at", "updated_at"]

    def validate_total_copies(self, value):
        if value < 1:
            raise serializers.ValidationError("A book must have at least 1 copy.")
        return value

    def create(self, validated_data):
        # A freshly-added book starts fully available.
        validated_data["available_copies"] = validated_data.get("total_copies", 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_total = validated_data.get("total_copies")
        if new_total is not None and new_total != instance.total_copies:
            issued_count = instance.total_copies - instance.available_copies
            if new_total < issued_count:
                raise serializers.ValidationError(
                    {
                        "total_copies": (
                            f"Cannot set total copies below {issued_count}, the number "
                            "currently issued out."
                        )
                    }
                )
            # Adjust available_copies by the same delta so the two stay in sync.
            instance.available_copies = new_total - issued_count
        return super().update(instance, validated_data)


class BookIssueSerializer(serializers.ModelSerializer):
    """Handles issuing a book to the logged-in user."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    is_returned = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    fine_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            "id",
            "user",
            "book",
            "book_title",
            "issue_date",
            "due_date",
            "return_date",
            "is_returned",
            "is_overdue",
            "fine_amount",
        ]
        read_only_fields = ["issue_date", "due_date", "return_date"]

    def validate_book(self, book):
        if not book.is_available:
            raise serializers.ValidationError("No copies of this book are currently available.")
        return book

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None:
            active_issues = BookIssue.objects.filter(user=user, return_date__isnull=True).count()
            if active_issues >= User.MAX_BOOKS_ALLOWED:
                raise serializers.ValidationError(
                    f"You already have {User.MAX_BOOKS_ALLOWED} books issued. "
                    "Return one before issuing another."
                )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        with transaction.atomic():
            # Lock the row so two concurrent issues can't both grab the last copy.
            book = Book.objects.select_for_update().get(pk=book.pk)
            if not book.is_available:
                raise serializers.ValidationError({"book": "No copies of this book are currently available."})
            book.available_copies -= 1
            book.save(update_fields=["available_copies"])
            issue = BookIssue.objects.create(user=user, book=book)
        return issue


class BookReturnSerializer(serializers.ModelSerializer):
    """Handles marking an existing BookIssue as returned."""

    is_overdue = serializers.BooleanField(read_only=True)
    fine_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            "id",
            "book",
            "user",
            "issue_date",
            "due_date",
            "return_date",
            "is_overdue",
            "fine_amount",
        ]
        read_only_fields = ["book", "user", "issue_date", "due_date", "return_date"]

    def update(self, instance, validated_data):
        if instance.is_returned:
            raise serializers.ValidationError("This book has already been returned.")
        with transaction.atomic():
            instance.return_date = datetime.date.today()
            instance.save(update_fields=["return_date"])
            book = instance.book
            book.available_copies += 1
            book.save(update_fields=["available_copies"])
        return instance

class TopBookSerializer(serializers.ModelSerializer):

    issued_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "issued_count"
        ]

