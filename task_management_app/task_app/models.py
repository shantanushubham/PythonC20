import uuid
from django.db import models


class Task(models.Model):
  class Status(models.TextChoices):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  owner = models.CharField(max_length=255)
  title = models.CharField(max_length=255)
  description = models.TextField()
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
  created_at = models.DateField(auto_now_add=True)
  due_at = models.DateField()

  def save(self, *args, **kwargs):
    if self.due_at and self.created_at and self.due_at <= self.created_at:
      raise ValueError("due_at must be after created_at")
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.title} ({self.owner})"


task = Task()
# Now we want to send the task object in response
# return Response(status=200, data=task)
# task will be serialised into JSON to be sent as Response Data.

# Python or Django doesn't know how to serialise/deserialise Task
# So, the developer needs to interfere to tell Python or Django how to serialise/deseriaise Task
