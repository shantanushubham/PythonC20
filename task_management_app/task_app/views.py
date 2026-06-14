import logging

from asgiref.sync import sync_to_async
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
from task_app.tasks import process_event
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
            tasks = Task.objects.filter(status=status_filter)
        else:
            tasks = Task.objects.all()

        logger.info("op=list status=success count=%s", tasks.count())
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
    @action(detail=True, methods=["POST"], url_path="mark_complete")
    def mark_complete(self, request, pk=None):
        logger.info("op=mark_complete task_id=%s user_id=%s", pk, request.user.id)
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            logger.warning("op=mark_complete status=failed reason=task_not_found task_id=%s", pk)
            return Response(data={"error": "Task not found"}, status=404)

        if task.status == Task.Status.DONE:
            logger.info("op=mark_complete status=skipped reason=already_complete task_id=%s", pk)
            return Response(
                data={"message": "Task is already marked as complete"}, status=200
            )

        task.status = Task.Status.DONE
        task.save()
        serializer = TaskSerialiser(task)
        logger.info("op=mark_complete status=success task_id=%s", pk)
        return Response(
            data={"message": "Task marked as complete", "task": serializer.data},
            status=200,
        )

    # GET /tasks/in_progress/
    @action(detail=False, methods=["GET"], url_path="in_progress")
    def test_function(self, request):
        logger.info("op=test_function user_id=%s", request.user.id)
        try:
            rows = list(
                Task.objects.filter(
                    status=Task.Status.IN_PROGRESS,
                    owner__first_name="Ananya",
                    owner__last_name="Gupta",
                ).values()
            )
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

class ProduceEventView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        message = request.data.get("message")
        logger.info("op=post view=ProduceEventView message=%s", message)
        if not message:
            return Response(data={"error": "'message' field is required"}, status=400)
        result = process_event.delay(message)
        logger.info("op=post view=ProduceEventView status=success task_id=%s", result.id)
        return Response(data={"task_id": result.id}, status=202)


# Tasks:
# 1. Task priority — add a priority field (LOW, MEDIUM, HIGH) to the Task model, 
#    filter by it the same way status filtering is already done.
# 2. Overdue tasks endpoint — GET /tasks/overdue/ — return tasks 
#    where due_at < today and status != DONE
# 3. Write tests (using AI is fine)


async def read():
    tasks = sync_to_async(Task.objects.all())

read()
