from rest_framework import serializers
from .models import Assignment, Enrollment, Lecture, Student, Subject, TeachingAssignment


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = TeachingAssignment
        fields = ("id", "subject")


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "student", "teaching_assignment")


class BulkEnrollmentSerializer(serializers.Serializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), many=True
    )


class LectureSerializer(serializers.ModelSerializer):
    teaching_assignment = serializers.PrimaryKeyRelatedField(
        queryset=TeachingAssignment.objects.all()
    )

    class Meta:
        model = Lecture
        fields = ("id", "teaching_assignment", "title", "description", "uploaded_at")
        read_only_fields = ("uploaded_at",)


class AssignmentSerializer(serializers.ModelSerializer):
    teaching_assignment = serializers.PrimaryKeyRelatedField(
        queryset=TeachingAssignment.objects.all()
    )

    class Meta:
        model = Assignment
        fields = (
            "id",
            "teaching_assignment",
            "title",
            "description",
            "deadline",
            "uploaded_at",
        )
        read_only_fields = ("uploaded_at",)
