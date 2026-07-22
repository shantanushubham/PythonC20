from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):

    message = "Only authenticated teachers van perform this task"

    """
        This permission class should only verify that the user is authenticated nad is a teacher
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(
            request.user, "teacher_profile"
        )
