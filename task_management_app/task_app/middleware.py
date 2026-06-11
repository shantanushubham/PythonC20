import logging
import re
import json
from django.http import HttpRequest, HttpResponse, JsonResponse

from task_app.utils import JWTUtil

logger = logging.getLogger(__name__)


class ValidateTaskIdMiddleware:
    TASK_ID_PATTERN = re.compile(r"^/tasks/(-?\d+)/$")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        match = self.TASK_ID_PATTERN.match(request.path)
        if match:
            task_id = int(match.group(1))
            logger.info("op=__call__ path=%s task_id=%s", request.path, task_id)
            if task_id <= 0:
                logger.warning(
                    "op=__call__ status=failed reason=invalid_task_id task_id=%s",
                    task_id,
                )
                return HttpResponse(
                    content=json.dumps({"error": "task_id must be a positive integer"}),
                    content_type="application/json",
                    status=400,
                )
        return self.get_response(request)


# class JWTAutheticationMiddleware:

#     def __init__(self, get_response) -> None:
#         self.get_response = get_response

#     def __call__(self, request):
#         if not request.path.startswith("/api/auth"):
#             token = request.headers.get("Authorization")
#             token = token[7:]  # Bearer gcwdkcjkdwchjw
#             token_verification_response = JWTUtil.verify_token(token)
#             if token_verification_response["valid"]:
#                 response = self.get_response(request)
#                 return response
#             else:
#                 return JsonResponse(status=401, data={"message": "Please use valid token"})
#         return self.get_response(request)
