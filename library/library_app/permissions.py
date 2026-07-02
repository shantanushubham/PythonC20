from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


class IsLibrarianOrReadOnly(BasePermission):
    """Any authenticated user can read (list/retrieve) books.
    Only a Librarian can create, update, or delete them."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(user, "role", None) == User.Role.LIBRARIAN
