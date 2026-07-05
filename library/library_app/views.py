from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .jwt_utils import generate_token
from .models import Book, BookIssue
from .permissions import IsLibrarianOrReadOnly
from .serializers import (
    BookIssueSerializer,
    BookReturnSerializer,
    BookSerializer,
    LoginSerializer,
    TopBookSerializer,
    UserSerializer,
)


class SignUpView(APIView):
    """Public endpoint to register a new user. `password` is write-only, so it
    never comes back in the response."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Public endpoint to log a user in. Issues a manually-signed JWT that must
    be sent as `Authorization: Bearer <token>` on subsequent requests."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = generate_token(user)
        return Response(
            {"token": token, "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Protected endpoint: proves JWTAuthentication is wired up correctly."""

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)


class BookViewSet(viewsets.ModelViewSet):
    """Full Book CRUD. Any authenticated user can list/retrieve; only a
    Librarian can create/update/delete (enforced by IsLibrarianOrReadOnly)."""

    queryset = Book.objects.all().order_by("title")
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]


class BookIssueView(APIView):
    """GET: list the current user's book issues (past and present), including
    the live-computed `fine_amount` for each -- this is how a user actually
    sees what they owe before returning a book.

    POST: issue a book (by id) to the currently logged-in user. All the
    actual business rules (max 5 active issues per user, copy availability,
    decrementing `available_copies` atomically) live in BookIssueSerializer
    so they can't be bypassed or duplicated elsewhere."""

    def get(self, request, *args, **kwargs):
        issues = BookIssue.objects.filter(user=request.user)
        return Response(
            BookIssueSerializer(issues, many=True, context={"request": request}).data
        )

    def post(self, request, *args, **kwargs):
        serializer = BookIssueSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()
        return Response(
            BookIssueSerializer(issue, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class BookReturnView(APIView):
    """Mark one of the current user's own book issues as returned.

    Scoped to `user=request.user` so nobody can return someone else's issue.
    All the mutation logic (guarding against double-return, incrementing
    `available_copies` atomically, computing the fine) lives in
    BookReturnSerializer."""

    def post(self, request, pk, *args, **kwargs):
        try:
            issue = BookIssue.objects.get(pk=pk, user=request.user)
        except BookIssue.DoesNotExist:
            raise NotFound("No such book issue found for this user.")

        serializer = BookReturnSerializer(issue, data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()

        data = BookReturnSerializer(issue, context={"request": request}).data
        if issue.fine_amount > 0:
            data["message"] = (
                f"Book returned late. A fine of Rs. {issue.fine_amount} has been levied."
            )
        else:
            data["message"] = "Book returned on time. No fine."
        return Response(data)


class MostIssuedBook(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        six_months_ago = timezone.now().date() - relativedelta(months=6)

        top_5_most_issued_books = Book.objects.annotate(
            issued_count=Count("issues", filter=Q(issues__issue_date__gte=six_months_ago))
        ).order_by("-issued_count")[:5]

        serializer = TopBookSerializer(top_5_most_issued_books, many=True)
        return Response(data=serializer.data, status=200)
