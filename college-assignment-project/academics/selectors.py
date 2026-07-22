from .models import Assignment, Enrollment, Lecture, TeachingAssignment


class TeachingAssignmentSelector:

    @staticmethod
    def get_all():
        return TeachingAssignment.objects.select_related("teacher__user", "subject")
    """
    1. SELECT * FROM teaching_assignment
    JOIN teacher
    JOIN user
    JOIN subject
    """

    @staticmethod
    def get_by_id(pk):
        return TeachingAssignment.objects.select_related(
            "teacher__user", "subject"
        ).get(pk=pk)


class EnrollmentSelector:

    @staticmethod
    def get_by_teaching_assignment(teaching_assignment):
        return Enrollment.objects.filter(
            teaching_assignment=teaching_assignment
        ).select_related("student__user", "teaching_assignment")


class LectureSelector:

    @staticmethod
    def get_by_teacher(teacher):
        return Lecture.objects.filter(
            teaching_assignment__teacher=teacher
        ).select_related("teaching_assignment__subject")


class AssignmentSelector:

    @staticmethod
    def get_by_teacher(teacher):
        return Assignment.objects.filter(
            teaching_assignment__teacher=teacher
        ).select_related("teaching_assignment__subject")
