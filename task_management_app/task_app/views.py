import json
import uuid
from rest_framework.decorators import api_view
from rest_framework.views import Request, Response

from task_app.models import Task
from task_app.serialisers import TaskSerialiser

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


@api_view(["GET"])
def add_two_numbers(request: Request):
    a = int(request.GET.get("a"))
    b = int(request.GET.get("b"))
    return Response(data={"sum": a + b}, status=200)


@api_view(["POST"])
def create_task(request: Request):
    task_serialiser = TaskSerialiser(data=request.data)
    if not task_serialiser.is_valid():
        return Response(status=400, data="Please send valid data")
    task = task_serialiser.save() # This will go and add to DB also
    return Response(data={"message": "Task Created", "task": task_serialiser.data}, status=201)


@api_view(["GET"])
def get_all_tasks(request: Request):
    tasks = Task.objects.all()
    task_serialiser = TaskSerialiser(tasks, many=True)
    return Response(data={"tasks": task_serialiser.data, "count": tasks.count()}, status=200)


@api_view(["GET", "PUT", "DELETE"])
def task_detail(request: Request, task_id: uuid):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(data={"error": "Task not found"}, status=404)

    if request.method == "GET":
        task_serialiser = TaskSerialiser(task)
        return Response(data={"task": task_serialiser.data}, status=200)

    if request.method == "PUT":
        task_serialiser = TaskSerialiser(task, data=request.data, partial=True)
        if not task_serialiser.is_valid():
            return Response(data=task_serialiser.errors, status=400)
        task_serialiser.save()
        return Response(data={"message": "Task Updated", "task": task_serialiser.data}, status=200)

    if request.method == "DELETE":
        task_data = TaskSerialiser(task).data
        task.delete()
        return Response(data={"message": "Task Deleted", "task": task_data}, status=200)
