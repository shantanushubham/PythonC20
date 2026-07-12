# College Portal

There are 3 kinds of users.
1. Student
2. Teacher
3. HOD - (is also a teacher)
4. Director
5. Department

Requirements:
1. A student studies multiple subjects. (Min 3 and Max 5)
2. According to the subject, a teacher may upload a lecture or an assignment.
  2.1. If its a lecture then the students are just notified.
  2.2. If its an assignment, then the student needs to submit it on time. In case of delay in submission, the student needs to justify the delay and the case goes to HOD. HOD can approve or reject the submission.
3. When an assignment is submitted, the teacher can review and provide remarks.
4. Director acts as an admin of the college and can see all the info
5. A student will always belong to a department.
6. A teacher may belong to multiple departments.
7. An HOD will always belong to only 1 department.
8. When a techaer is updated to HOD, we must check that they belong to only 1 department.

##### Notes
1. User [not a model, will act as a parent class]
```python
class User(AbstractUser):
  pass
```
2. Student
```python
class Student(models.Model):
  user = models.OneToOneField(user)
  department = models.ForeignKey(Department)
  roll_number = models.CharField(...)
```
3. Teacher
```python
class Teacher(models.Model):
    user = models.OneToOneField(User)
```
4. Department
```python
class Department(models.Model):
  name = models.CharField(...)  
  hod = models.OneToOneField(Teacher, on_delete=models.PROTECT)
```
5. Subject
```python
class Subject(models.Model):
  name = ...
  departments = models.ManyToManyField(Department,related_name="subjects")
```
6. Enrollment
```python
class Enrollment(models.Model):
  student = models.ForeginKey(Student)
  teaching_assignment = models.ForeignKey(TeachingAssignment, on_delete=models.CASCADE)
```
7. Content (ABC)
    |- Lecture
    |- Assignment
```python
class Content(models.Model):
  teaching_assignment = models.ForeignKey(TeachingAssignment, on_delete=models.CASCADE)
  title = ...
  description = ...
  uploaded_at = ...
  
  class Meta:
    abstract = True

class Lecture(Content):
  ...

class Assignment(Content):
  ...
```
8. AssignmentSubmission
9. SubmissionReview
10. DelayRequest
11. Notification
12. TeachinhgAssigment
```python
class TeachingAssignment(models.Model):
  teacher
  subject
```


ER MODEL
```
                                      +----------------------+
                                      |        User          |
                                      |----------------------|
                                      | id                   |
                                      | username             |
                                      | email                |
                                      | ...                  |
                                      +----------+-----------+
                                                 ^
                                                 |
                                  One-to-One     |
                        +------------------------+------------------------+
                        |                                                 |
                        |                                                 |
                +-------+--------+                               +--------+-------+
                |    Student     |                               |    Teacher     |
                |----------------|                               |----------------|
                | user_id        |                               | user_id        |
                | roll_number    |                               +--------+-------+
                | department_id  |                                        |
                +-------+--------+                                        |
                        |                                                 |
                        | N:1                                             |
                        |                                                 |
              +---------v------------------------+                        |
              |          Department             |<------------------------+
              |---------------------------------|      HOD (1:1)
              | id                              |
              | name                            |
              | hod_id                          |
              +---------+-----------------------+
                        ^
                        |
                        | M:N
                        |
                +-------+--------+
                |    Subject     |
                |----------------|
                | id             |
                | name           |
                +-------+--------+
                        ^
                        |
                        | 1:N
                        |
          +-------------+----------------------+
          |       TeachingAssignment          |
          |-----------------------------------|
          | id                                |
          | teacher_id                        |
          | subject_id                        |
          | (future: semester, section, etc.) |
          +-------------+---------------------+
                        ^
                        |
                  N:1   |
                 Enrollment
                        |
          +-------------+---------------------+
          | id                                |
          | student_id                        |
          | teaching_assignment_id            |
          +-------------+---------------------+
                        |
                        |
                     Student


                      TeachingAssignment
                     /                  \
                    /                    \
                   v                      v
           +---------------+      +----------------+
           |   Lecture     |      |   Assignment   |
           +-------+-------+      +-------+--------+
                                           |
                                           | 1:N
                                           |
                               +-----------v----------------+
                               | AssignmentSubmission       |
                               |----------------------------|
                               | assignment_id             |
                               | student_id                |
                               | submitted_at             |
                               | file                     |
                               | status                   |
                               +-----------+--------------+
                                           |
                      +--------------------+--------------------+
                      |                                         |
                      |                                         |
             +--------v---------+                     +---------v---------+
             | SubmissionReview |                     |  DelayRequest     |
             |------------------|                     |-------------------|
             | submission_id    |                     | submission_id     |
             | teacher_id       |                     | reason            |
             | remarks          |                     | status            |
             | marks            |                     | reviewed_by(HOD)  |
             +------------------+                     +-------------------+


User
  |
  | 1:N
  |
+------------------+
|   Notification   |
|------------------|
| recipient_id     |
| title            |
| message          |
| is_read          |
+------------------+
```

