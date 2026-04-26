import json
from rest_framework.decorators import api_view
from rest_framework.views import Request, Response

from task_app.my_classes import Task

TASKS_FILE = (
    "/Users/shantanu/B/AirTribe/PythonC20/task_management_app/task_app/data/tasks.json"
)


@api_view(["GET"])
def add_two_numbers(request: Request):
    # Take values from Query Parameters
    a = int(request.GET.get("a"))
    b = int(request.GET.get("b"))
    # Return sum in Response
    return Response(data={"sum": a + b}, status=200)


@api_view(["POST"])
def create_task(request: Request):
    data = request.data
    task = Task(
        owner=data["owner"],
        title=data["title"],
        description=data["description"],
        due_at=data["due_at"],
    )
    create_task_in_file(task)
    return Response(data={"message": "Task Created", "task": task.__dict__}, status=201)


def create_task_in_file(task: Task):
    with open(TASKS_FILE, "r") as file:
        content = file.read()
        # tasks = content.strip() ? json.loads(content) : []
        tasks: list[dict] = json.loads(content) if content.strip() else []
    tasks.append(task.__dict__)

    with open(TASKS_FILE, "w") as file:
        file.write(json.dumps(tasks, default=str, indent=2))
