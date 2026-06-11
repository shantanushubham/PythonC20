import logging

from django.db import connection
from rest_framework.decorators import action
from rest_framework.views import APIView, Request, Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from task_app.models import Task, User
from task_app.permissions import TestPermission
from task_app.serialisers import (
    LoginSerialiser,
    SignUpSerialiser,
    TaskSerialiser,
    UserSerialiser,
)
from task_app.utils import JWTUtil

logger = logging.getLogger(__name__)


class TaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerialiser
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]

    # GET /tasks/?status=PENDING
    # Uses Model.objects.raw() — returns model instances, works directly with the serialiser.
    def list(self, request):
        status_filter = request.query_params.get("status")
        logger.info("op=list status_filter=%s user_id=%s", status_filter, request.user.id)

        if status_filter is not None:
            status_filter = status_filter.upper()
            valid_statuses = Task.Status.values
            if status_filter not in valid_statuses:
                logger.warning(
                    "op=list status=failed reason=invalid_status value=%s",
                    status_filter,
                )
                return Response(
                    data={
                        "error": f"Invalid status. Choose from: {', '.join(valid_statuses)}"
                    },
                    status=400,
                )
            # Raw SQL with a parameterised WHERE clause (%s prevents SQL injection)
            tasks = list(
                Task.objects.raw(
                    "SELECT * FROM task_app_task WHERE status = %s", [status_filter]
                )
            )
        else:
            tasks = list(Task.objects.raw("SELECT * FROM task_app_task"))

        logger.info("op=list status=success count=%s", len(tasks))
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskSerialiser(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskSerialiser(tasks, many=True)
        return Response(serializer.data, status=200)

    def perform_create(self, serializer):
        logger.info("op=perform_create user_id=%s", self.request.user.id)
        serializer.save(owner=self.request.user)
        logger.info("op=perform_create status=success task_id=%s", serializer.instance.id)

    # POST /tasks/<pk>/mark_complete/
    # Uses connection.cursor() — direct cursor execution for UPDATE.
    @action(detail=True, methods=["POST"], url_path="mark_complete")
    def mark_complete(self, request, pk=None):
        logger.info("op=mark_complete task_id=%s user_id=%s", pk, request.user.id)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, status FROM task_app_task WHERE id = %s", [pk])
            row = cursor.fetchone()

        if not row:
            logger.warning("op=mark_complete status=failed reason=task_not_found task_id=%s", pk)
            return Response(data={"error": "Task not found"}, status=404)

        _task_id, task_status = row
        if task_status == Task.Status.DONE:
            logger.info("op=mark_complete status=skipped reason=already_complete task_id=%s", pk)
            return Response(
                data={"message": "Task is already marked as complete"}, status=200
            )

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE task_app_task SET status = %s WHERE id = %s",
                [Task.Status.DONE, pk],
            )

        # Fetch the updated row as a model instance to pass into the serialiser
        updated_task = Task.objects.raw(
            "SELECT * FROM task_app_task WHERE id = %s", [pk]
        )[0]
        serializer = TaskSerialiser(updated_task)
        logger.info("op=mark_complete status=success task_id=%s", pk)
        return Response(
            data={"message": "Task marked as complete", "task": serializer.data},
            status=200,
        )

    # GET /tasks/in_progress/
    # Uses connection.cursor() with a JOIN — returns raw column data as dicts.
    @action(detail=False, methods=["GET"], url_path="in_progress")
    def test_function(self, request):
        logger.info("op=test_function user_id=%s", request.user.id)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT t.*
                    FROM task_app_task t
                    INNER JOIN task_app_user u ON t.owner_id = u.id
                    WHERE t.status = %s
                      AND CONCAT(u.first_name, ' ', u.last_name) = %s
                """,
                    [Task.Status.IN_PROGRESS, "Ananya Gupta"],
                )

                columns = [col.name for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            logger.info("op=test_function status=success count=%s", len(rows))
            return Response(data=rows, status=200)
        except Exception as e:
            logger.error("op=test_function status=failed reason=%s", e)
            return Response(data={"error": str(e)}, status=500)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerialiser


class LoginView(APIView):

    authentication_classes = []

    def post(self, request: Request):
        username = request.data.get("username")
        logger.info("op=post view=LoginView username=%s", username)
        serialiser = LoginSerialiser(data=request.data)
        if not serialiser.is_valid():
            logger.warning("op=post view=LoginView status=failed reason=validation_error username=%s", username)
            return Response(data=serialiser.errors, status=400)
        user = serialiser.validated_data["user"]
        token = JWTUtil.create_token(user.id)
        logger.info("op=post view=LoginView status=success user_id=%s", user.id)
        return Response(
            data={"user": UserSerialiser(user).data, "token": token}, status=200
        )


class SignUpView(APIView):

    authentication_classes = []

    def post(self, request: Request):
        username = request.data.get("username")
        logger.info("op=post view=SignUpView username=%s", username)
        serialiser = SignUpSerialiser(data=request.data)
        if not serialiser.is_valid():
            logger.warning("op=post view=SignUpView status=failed reason=validation_error username=%s", username)
            return Response(data=serialiser.errors, status=400)
        user = serialiser.save()
        token = JWTUtil.create_token(user.id)
        logger.info("op=post view=SignUpView status=success user_id=%s", user.id)
        return Response(
            data={"user": UserSerialiser(user).data, "token": token}, status=201
        )

# Tasks:
# 1. Task priority — add a priority field (LOW, MEDIUM, HIGH) to the Task model, 
#    filter by it the same way status filtering is already done.
# 2. Overdue tasks endpoint — GET /tasks/overdue/ — return tasks 
#    where due_at < today and status != DONE
# 3. Write tests (using AI is fine)
