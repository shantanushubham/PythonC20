import json
import uuid
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action, api_view
from rest_framework.views import Request, Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from task_app import serialisers
from task_app.models import Task
from task_app.serialisers import TaskSerialiser


class TaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50

TASKS_FILE = (
    "/Users/shantanu/B/AirTribe/PythonC20/task_management_app/task_app/data/tasks.json"
)

UPDATABLE_FIELDS = {"owner", "title", "description", "due_at", "status"}


def read_tasks() -> list[dict]:
    with open(TASKS_FILE, "r") as file:
        content = file.read()
    return json.loads(content) if content.strip() else []


def write_tasks(tasks: list[dict]):
    with open(TASKS_FILE, "w") as file:
        file.write(json.dumps(tasks, default=str, indent=2))


@extend_schema(
    summary="Add two numbers",
    parameters=[
        OpenApiParameter(name="a", type=int, location=OpenApiParameter.QUERY, required=True, description="First number"),
        OpenApiParameter(name="b", type=int, location=OpenApiParameter.QUERY, required=True, description="Second number"),
    ],
    responses=inline_serializer(
        name="AddTwoNumbersResponse",
        fields={"sum": drf_serializers.IntegerField()},
    ),
)
@api_view(["GET"])
def add_two_numbers(request: Request):
    a = int(request.GET.get("a"))
    b = int(request.GET.get("b"))
    return Response(data={"sum": a + b}, status=200)


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerialiser
    pagination_class = TaskPagination

    # GET /tasks/?status=PENDING
    def list(self, request):
        queryset = Task.objects.all()

        status_filter = request.query_params.get("status")
        if status_filter is not None:
            status_filter = status_filter.upper()
            valid_statuses = Task.Status.values
            if status_filter not in valid_statuses:
                return Response(
                    data={"error": f"Invalid status. Choose from: {', '.join(valid_statuses)}"},
                    status=400,
                )
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TaskSerialiser(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskSerialiser(queryset, many=True)
        return Response(serializer.data, status=200)

    # # GET /tasks/<pk>/
    def retrieve(self, request, pk=None):
        try:
            # task = Task.objects.get(id=pk)
            # serializer = TaskSerialiser(task)
            # return Response(serializer.data, status=200)
            return Response(data={"message": "Hello World"}, status=200)
        except Task.DoesNotExist:
            return Response(data={"error": "Task not found"}, status=404)


    # POST /tasks/views/<pk>/mark_complete/
    @action(detail=True, methods=["POST"], url_path="mark_complete")
    def mark_complete(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response(data={"error": "Task not found"}, status=404)
        if task.status == Task.Status.DONE:
            return Response(data={"message": "Task is already marked as complete"}, status=200)
        task.status = Task.Status.DONE
        task.save()
        serializer = TaskSerialiser(task)
        return Response(data={"message": "Task marked as complete", "task": serializer.data}, status=200)

    # # POST /tasks/
    # def create(self, request):
    #     serializer = TaskSerialiser(data=request.data)
    #     if not serializer.is_valid():
    #         return Response(data=serializer.errors, status=400)
    #     serializer.save()
    #     return Response(data={"message": "Task created", "task": serializer.data}, status=201)

    # # PUT /tasks/<pk>/
    # def update(self, request, pk=None):
    #     try:
    #         task = Task.objects.get(id=pk)
    #     except Task.DoesNotExist:
    #         return Response(data={"error": "Task not found"}, status=404)
    #     serializer = TaskSerialiser(task, data=request.data)
    #     if not serializer.is_valid():
    #         return Response(data=serializer.errors, status=400)
    #     serializer.save()
    #     return Response(data={"message": "Task updated", "task": serializer.data}, status=200)

    # # PATCH /tasks/<pk>/
    # def partial_update(self, request, pk=None):
    #     try:
    #         task = Task.objects.get(id=pk)
    #     except Task.DoesNotExist:
    #         return Response(data={"error": "Task not found"}, status=404)
    #     serializer = TaskSerialiser(task, data=request.data, partial=True)
    #     if not serializer.is_valid():
    #         return Response(data=serializer.errors, status=400)
    #     serializer.save()
    #     return Response(data={"message": "Task updated", "task": serializer.data}, status=200)

    # # DELETE /tasks/<pk>/
    # def destroy(self, request, pk=None):
    #     try:
    #         task = Task.objects.get(id=pk)
    #     except Task.DoesNotExist:
    #         return Response(data={"error": "Task not found"}, status=404)
    #     task_data = TaskSerialiser(task).data
    #     task.delete()
    #     return Response(data={"message": "Task deleted", "task": task_data}, status=200)


# Activity
# 1. Create an API that Fetches all tasks of a given user
# 2. Create an API that fetches the upcoming tasks of a user that are PENDING.
# 3. Create an API that fetches all the completed tasks in a gievn date range, for a given user.
