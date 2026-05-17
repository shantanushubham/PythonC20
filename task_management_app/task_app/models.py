from datetime import date
import uuid
from django.db import models

class User(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    dob = models.DateField()
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
      today = date.today()
      current_year = today.year
      birth_year = self.dob.year
      if current_year - birth_year < 18:
        raise ValueError("Age is less than 18")

      elif current_year - birth_year == 18:
        if today.month == self.dob.month:
          if today.day < self.dob.day:
            raise ValueError("Age is less than 18")
        elif today.month < self.dob.month:
          raise ValueError("Age is less than 18")
      
      super().save(*args, **kwargs)

    def __str__(self):
      return f"{self.first_name} {self.last_name}"


class Task(models.Model):
  class Status(models.TextChoices):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
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


# Now we want to send the task object in response
# return Response(status=200, data=task)
# task will be serialised into JSON to be sent as Response Data.



# Python or Django doesn't know how to serialise/deserialise Task
# So, the developer needs to interfere to tell Python or Django how to serialise/deseriaise Task



# Not necessarily related to Python
# There is a class called Object
# The Object class is the parent all classes by Default
# The Object class has a toString() function
# Because of Inheritance, every class has a toString() function
# A developer can override the toString Function if they want - function overriding

# If the developer doesn't override, python or Java will print the memory adress of the object. 
# Eg: print(user) --> Shantanu Shubham