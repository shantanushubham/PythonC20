from rest_framework import serializers
from .models import Task


class TaskSerialiser(serializers.ModelSerializer):
  class Meta:
    model = Task
    fields = ["id", "owner", "title", "description", "status", "created_at", "due_at"]
    read_only_fields = ["id", "created_at"]

  def validate_due_at(self, value):
    import datetime
    if value <= datetime.date.today():
      raise serializers.ValidationError("due_at must be a future date.")
    return value
