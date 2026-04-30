import json
from rest_framework.decorators import api_view
from rest_framework.views import Request, Response

from task_app.my_classes import Task

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
    data = request.data
    task = Task(
        id=data["id"],
        owner=data["owner"],
        title=data["title"],
        description=data["description"],
        due_at=data["due_at"],
    )
    tasks = read_tasks()
    tasks.append(task.__dict__)
    write_tasks(tasks)
    return Response(data={"message": "Task Created", "task": task.__dict__}, status=201)


@api_view(["GET"])
def get_all_tasks(request: Request):
    tasks = read_tasks()
    return Response(data={"tasks": tasks, "count": len(tasks)}, status=200)


@api_view(["GET", "PUT", "DELETE"])
def task_detail(request: Request, task_id: int):
    tasks = read_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t["id"] == task_id), None)

    if task_index is None:
        return Response(data={"error": f"Task with id {task_id} not found"}, status=404)

    if request.method == "GET":
        return Response(data={"task": tasks[task_index]}, status=200)

    if request.method == "PUT":
        task = tasks[task_index]
        for field, value in request.data.items():
            if field in UPDATABLE_FIELDS:
                task[field] = value
        write_tasks(tasks)
        return Response(data={"message": "Task Updated", "task": task}, status=200)

    if request.method == "DELETE":
        deleted = tasks.pop(task_index)
        write_tasks(tasks)
        return Response(data={"message": "Task Deleted", "task": deleted}, status=200)
