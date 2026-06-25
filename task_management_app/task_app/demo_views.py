import asyncio
import logging
import time

from asgiref.sync import sync_to_async
from rest_framework.views import APIView, Response

from task_app.models import Task

logger = logging.getLogger(__name__)


def _fetch_tasks_sync():
    """Sync ORM call — blocks the current worker thread until the DB responds."""
    time.sleep(1)
    return list(Task.objects.values_list("title", flat=True)[:5])


async def _fetch_tasks_async():
    """Async ORM call — await lets other requests run while waiting on I/O."""
    await asyncio.sleep(1)
    return [title async for title in Task.objects.values_list("title", flat=True)[:5]]


class SyncTaskDemoView(APIView):
    """
    GET /api/demo/sync-tasks/

    Runs two task queries one after another (~2s).
    Same execution model as TaskViewSet.list — sync def, blocking ORM.
    """

    authentication_classes = []

    def get(self, request):
        logger.info("op=get view=SyncTaskDemoView")
        start = time.perf_counter()

        first_batch = _fetch_tasks_sync()
        second_batch = _fetch_tasks_sync()

        elapsed = time.perf_counter() - start
        logger.info("op=get view=SyncTaskDemoView status=success elapsed=%.2fs", elapsed)
        return Response(
            data={
                "execution_mode": "sync",
                "description": "Two blocking queries run sequentially",
                "elapsed_seconds": round(elapsed, 2),
                "first_batch": first_batch,
                "second_batch": second_batch,
            },
            status=200,
        )


class AsyncTaskDemoView(APIView):
    """
    GET /api/demo/async-tasks/

    Runs two task queries concurrently (~1s).
    Requires an ASGI server (e.g. uvicorn task_app.asgi:application).
    """

    authentication_classes = []

    async def get(self, request):
        logger.info("op=get view=AsyncTaskDemoView")
        start = time.perf_counter()

        first_batch, second_batch = await asyncio.gather(
            _fetch_tasks_async(),
            _fetch_tasks_async(),
        )
        task_count = await Task.objects.acount()

        elapsed = time.perf_counter() - start
        logger.info("op=get view=AsyncTaskDemoView status=success elapsed=%.2fs", elapsed)
        return Response(
            data={
                "execution_mode": "async",
                "description": "Two async queries run concurrently with await",
                "elapsed_seconds": round(elapsed, 2),
                "first_batch": first_batch,
                "second_batch": second_batch,
                "task_count": task_count,
            },
            status=200,
        )


class AsyncSyncToAsyncDemoView(APIView):
    """
    GET /api/demo/sync-to-async/

    Shows how to call sync ORM safely from an async view.
    """

    authentication_classes = []

    async def get(self, request):
        logger.info("op=get view=AsyncSyncToAsyncDemoView")
        task_count = await sync_to_async(Task.objects.count)()
        logger.info("op=get view=AsyncSyncToAsyncDemoView status=success count=%s", task_count)
        return Response(
            data={
                "execution_mode": "async_with_sync_to_async",
                "description": "Sync ORM wrapped with sync_to_async for use in async views",
                "task_count": task_count,
            },
            status=200,
        )


class GracefulShutdownDemoView(APIView):
    """
    POST /api/demo/graceful-shutdown/

    Simulates slow work with time.sleep so you can demo graceful shutdown:
    start this endpoint, run the Go load generator, then Ctrl+C the server.
    In-flight requests should finish; new ones should fail to connect.
    """

    authentication_classes = []
    permission_classes = []
    DEFAULT_SLEEP_SECONDS = 5
    MAX_SLEEP_SECONDS = 30

    def post(self, request):
        raw_seconds = request.data.get("seconds", self.DEFAULT_SLEEP_SECONDS)
        try:
            sleep_seconds = float(raw_seconds)
        except (TypeError, ValueError):
            return Response(
                data={"error": "'seconds' must be a number"},
                status=400,
            )

        if sleep_seconds <= 0 or sleep_seconds > self.MAX_SLEEP_SECONDS:
            return Response(
                data={
                    "error": f"'seconds' must be between 0 (exclusive) and {self.MAX_SLEEP_SECONDS}"
                },
                status=400,
            )

        request_id = request.headers.get("X-Request-Id", "unknown")
        started_at = time.time()
        logger.info(
            "op=post view=GracefulShutdownDemoView status=started request_id=%s sleep_seconds=%s",
            request_id,
            sleep_seconds,
        )

        time.sleep(sleep_seconds)

        elapsed = round(time.time() - started_at, 2)
        logger.info(
            "op=post view=GracefulShutdownDemoView status=completed request_id=%s elapsed=%ss",
            request_id,
            elapsed,
        )
        return Response(
            data={
                "status": "completed",
                "request_id": request_id,
                "sleep_seconds": sleep_seconds,
                "elapsed_seconds": elapsed,
                "message": "Request finished — server waited for this before shutting down",
            },
            status=200,
        )
