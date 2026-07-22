from .models import Assignment, Enrollment, Lecture, TeachingAssignment


class TeachingAssignmentService:

    @staticmethod
    def create(*, teacher, subject):
        return TeachingAssignment.objects.create(teacher=teacher, subject=subject)

    @staticmethod
    def update(*, teaching_assignment, subject):
        teaching_assignment.subject = subject
        teaching_assignment.save()
        return teaching_assignment

    @staticmethod
    def delete(*, teaching_assignment):
        teaching_assignment.delete()


class EnrollmentService:

    @staticmethod
    def bulk_create(*, teaching_assignment, students):
        existing_student_ids = set(
            Enrollment.objects.filter(
                teaching_assignment=teaching_assignment, student__in=students
            ).values_list("student_id", flat=True)
        )

        new_enrollments = []
        for student in students:
            if student.id not in existing_student_ids:
                new_enrollments.append(
                    Enrollment(student=student, teaching_assignment=teaching_assignment)
                )

        return Enrollment.objects.bulk_create(new_enrollments)


class LectureService:

    @staticmethod
    def create(*, teaching_assignment, title, description):
        return Lecture.objects.create(
            teaching_assignment=teaching_assignment,
            title=title,
            description=description,
        )

    @staticmethod
    def update(*, lecture, title, description):
        lecture.title = title
        lecture.description = description
        lecture.save()
        return lecture

    @staticmethod
    def delete(*, lecture):
        lecture.delete()


class AssignmentService:

    @staticmethod
    def create(*, teaching_assignment, title, description, deadline):
        return Assignment.objects.create(
            teaching_assignment=teaching_assignment,
            title=title,
            description=description,
            deadline=deadline,
        )

    @staticmethod
    def update(*, assignment, title, description, deadline):
        assignment.title = title
        assignment.description = description
        assignment.deadline = deadline
        assignment.save()
        return assignment

    @staticmethod
    def delete(*, assignment):
        assignment.delete()
