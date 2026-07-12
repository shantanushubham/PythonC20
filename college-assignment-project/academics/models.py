from django.db import models
from django.conf import settings

# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    department = models.ForeignKey(
        "Department", on_delete=models.PROTECT, related_name="students"
    )

    roll_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    employee_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    hod = models.OneToOneField(
        "Teacher",
        on_delete=models.PROTECT,
        related_name="headed_department",
        null=True,
        blank=True,
    )


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    departments = models.ManyToManyField(Department, related_name="subjects")

    def __str__(self):
        return self.name


class TeachingAssignment(models.Model):
    teacher: Teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="teaching_assignments"
    )

    subject: Subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="teaching_assignments"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject"], name="unique_teacher_subject_assignment"
            )
        ]

    def __str__(self) -> str:
        return f"{self.teacher}" - {self.subject}


class Enrollment(models.Model):
    student: Student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments"
    )

    teaching_assignment: TeachingAssignment = models.ForeignKey(
        TeachingAssignment, on_delete=models.CASCADE, related_name="enrollments"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "teaching_assignment"],
                name="unique_student_teaching_assignment",
            )
        ]

    def __str__(self):
        return f"{self.student} -> {self.teaching_assignment.subject}"


class AcademicContent(models.Model):
    teaching_assignment = models.ForeignKey(
        TeachingAssignment, on_delete=models.CASCADE, related_name="%(class)ss"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Lecture(AcademicContent):

    def __str__(self):
        return self.title


class Assignment(AcademicContent):
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUBMITTED = "SUBMITTED", "Submitted"
        LATE = "LATE", "Late"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="submissions"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=28, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"], name="unique_assignment_submission"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.assignment}"


class DelayRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    submission = models.OneToOneField(
        AssignmentSubmission, on_delete=models.CASCADE, related_name="delay_request"
    )

    reason = models.TextField()

    reviewed_by = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="reviewed_delay_requests"
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return f"Delay Request - {self.submission}"


class SubmissionReview(models.Model):
    submission = models.OneToOneField(
        AssignmentSubmission, on_delete=models.CASCADE, related_name="review"
    )

    teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name="submission_reviews"
    )

    remarks = models.TextField()

    marks = models.PositiveIntegerField()

    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review - {self.submission}"

