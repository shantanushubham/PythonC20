from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from academics.models import TeachingAssignment
from academics.permissions import IsTeacher
from academics.selectors import (
    AssignmentSelector,
    EnrollmentSelector,
    LectureSelector,
    TeachingAssignmentSelector,
)
from academics.serializers import (
    AssignmentSerializer,
    BulkEnrollmentSerializer,
    EnrollmentSerializer,
    LectureSerializer,
    TeachingAssignmentSerializer,
)
from academics.services import (
    AssignmentService,
    EnrollmentService,
    LectureService,
    TeachingAssignmentService,
)


def _assert_owns_teaching_assignment(request, teaching_assignment):
    if teaching_assignment.teacher_id != request.user.teacher_profile.id:
        raise PermissionDenied(
            "You can only manage content for your own teaching assignments."
        )


class TeachingAssignmentModelViewSet(ModelViewSet):

    serializer_class = TeachingAssignmentSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return TeachingAssignment.objects.filter(
            teacher=self.request.user.teacher_profile
        ).select_related("teacher", "subject")

    def perform_create(self, serializer):
        TeachingAssignmentService.create(
            teacher=self.request.user.teacher_profile,
            subject=serializer.validated_data["subject"],
        )

    def perform_update(self, serializer):
        TeachingAssignmentService.update(
            teaching_assignment=self.get_object(),
            subject=serializer.validated_data["subject"],
        )

    def perform_destroy(self, instance):
        TeachingAssignmentService.delete(teaching_assignment=instance)

    @action(detail=True, methods=["post"], url_path="enrollments")
    def enrollments(self, request, pk=None):
        """Bulk-enroll students into this teaching assignment.

        Only the teacher who owns this teaching assignment can enroll
        students into it, since `get_object` is scoped to `get_queryset`.
        """
        teaching_assignment = self.get_object()

        input_serializer = BulkEnrollmentSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        created_enrollments = EnrollmentService.bulk_create(
            teaching_assignment=teaching_assignment,
            students=input_serializer.validated_data["students"],
        )

        output_serializer = EnrollmentSerializer(created_enrollments, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @enrollments.mapping.get
    def list_enrollments(self, request, pk=None):
        teaching_assignment = self.get_object()
        enrollments = EnrollmentSelector.get_by_teaching_assignment(
            teaching_assignment
        )
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class LectureModelViewSet(ModelViewSet):
    """Lets a teacher create and manage lecture content for their own
    teaching assignments."""

    serializer_class = LectureSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return LectureSelector.get_by_teacher(self.request.user.teacher_profile)

    def perform_create(self, serializer):
        teaching_assignment = serializer.validated_data["teaching_assignment"]
        _assert_owns_teaching_assignment(self.request, teaching_assignment)
        serializer.instance = LectureService.create(
            teaching_assignment=teaching_assignment,
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
        )

    def perform_update(self, serializer):
        _assert_owns_teaching_assignment(
            self.request, serializer.validated_data["teaching_assignment"]
        )
        serializer.instance = LectureService.update(
            lecture=self.get_object(),
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
        )

    def perform_destroy(self, instance):
        LectureService.delete(lecture=instance)


class AssignmentModelViewSet(ModelViewSet):
    """Lets a teacher create and manage assignments for their own
    teaching assignments."""

    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return AssignmentSelector.get_by_teacher(self.request.user.teacher_profile)

    def perform_create(self, serializer):
        teaching_assignment = serializer.validated_data["teaching_assignment"]
        _assert_owns_teaching_assignment(self.request, teaching_assignment)
        serializer.instance = AssignmentService.create(
            teaching_assignment=teaching_assignment,
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            deadline=serializer.validated_data["deadline"],
        )

    def perform_update(self, serializer):
        _assert_owns_teaching_assignment(
            self.request, serializer.validated_data["teaching_assignment"]
        )
        serializer.instance = AssignmentService.update(
            assignment=self.get_object(),
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            deadline=serializer.validated_data["deadline"],
        )

    def perform_destroy(self, instance):
        AssignmentService.delete(assignment=instance)
