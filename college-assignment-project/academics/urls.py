from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentModelViewSet,
    LectureModelViewSet,
    TeachingAssignmentModelViewSet,
)

router = DefaultRouter()

router.register(
    "teaching_assignments",
    TeachingAssignmentModelViewSet,
    basename="teaching-assignment",
)

router.register(
    "lectures",
    LectureModelViewSet,
    basename="lecture",
)

router.register(
    "assignments",
    AssignmentModelViewSet,
    basename="assignment",
)

urlpatterns = [path("", include(router.urls))]
