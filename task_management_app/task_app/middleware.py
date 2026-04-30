import re
import json
from django.http import HttpRequest, HttpResponse


class ValidateTaskIdMiddleware:
    TASK_ID_PATTERN = re.compile(r"^/tasks/(-?\d+)/$")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        match = self.TASK_ID_PATTERN.match(request.path)
        if match:
            task_id = int(match.group(1))
            if task_id <= 0:
                return HttpResponse(
                    content=json.dumps({"error": "task_id must be a positive integer"}),
                    content_type="application/json",
                    status=400,
                )
        return self.get_response(request)
