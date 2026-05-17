from rest_framework import serializers

from task_app.utils import BCruptUtil
from .models import Task, User


class TaskOwnerSerialiser(serializers.ModelSerializer):
  name = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ["id", "name"]

  def get_name(self, obj):
    return f"{obj.first_name} {obj.last_name}"


class TaskSerialiser(serializers.ModelSerializer):
  owner = TaskOwnerSerialiser(read_only=True)
  owner_id = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), source="owner", write_only=True
  )

  class Meta:
    model = Task
    fields = ["id", "owner", "owner_id", "title", "description", "status", "created_at", "due_at"]
    read_only_fields = ["id", "created_at"]

  def validate_due_at(self, value):
    import datetime
    if value <= datetime.date.today():
      raise serializers.ValidationError("due_at must be a future date.")
    return value


class UserSerialiser(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ["id", "first_name", "last_name", "dob", "username", "password"]
    read_only_fields = ["id"]


class SignUpSerialiser(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ["id", "first_name", "last_name", "dob", "username", "password"]
    read_only_fields = ["id"]

  def create(self, validated_data):
    validated_data["password"] = BCruptUtil.encrypt_password(validated_data["password"])
    return User.objects.create(**validated_data)


class LoginSerialiser(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True)

  def validate(self, data):
    username = data.get("username")
    password = data.get("password")

    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      raise serializers.ValidationError("Invalid username or password.")

    if not BCruptUtil.verify_password(password, user.password):
      raise serializers.ValidationError("Invalid username or password.")

    data["user"] = user
    return data


