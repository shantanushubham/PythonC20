from django.contrib import admin

from .models import Book, BookIssue, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")
    exclude = ("password",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "available_copies", "total_copies")
    search_fields = ("title", "author", "isbn")


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "issue_date", "due_date", "return_date")
    list_filter = ("issue_date", "return_date")
