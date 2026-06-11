import logging

from rest_framework import serializers

from task_app.utils import BCruptUtil
from .models import Task, User

logger = logging.getLogger(__name__)


class TaskOwnerSerialiser(serializers.ModelSerializer):
  name = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ["id", "name"]

  def get_name(self, obj):
    logger.info("op=get_name user_id=%s", obj.id)
    return f"{obj.first_name} {obj.last_name}"


class TaskSerialiser(serializers.ModelSerializer):
  owner = TaskOwnerSerialiser(read_only=True)
  owner_id = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), source="owner", write_only=True, required=False
  )

  class Meta:
    model = Task
    fields = ["id", "owner", "owner_id", "title", "description", "status", "created_at", "due_at"]
    read_only_fields = ["id", "created_at"]

  def validate_due_at(self, value):
    import datetime
    if value <= datetime.date.today():
      logger.warning("op=validate_due_at status=failed reason=not_future_date value=%s", value)
      raise serializers.ValidationError("due_at must be a future date.")
    logger.info("op=validate_due_at status=success value=%s", value)
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

  def validate_dob(self, value):
    import datetime
    today = datetime.date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
      logger.warning("op=validate_dob status=failed reason=underage dob=%s age=%s", value, age)
      raise serializers.ValidationError("User must be at least 18 years old.")
    logger.info("op=validate_dob status=success dob=%s age=%s", value, age)
    return value

  def create(self, validated_data):
    logger.info("op=create username=%s", validated_data.get("username"))
    validated_data["password"] = BCruptUtil.encrypt_password(validated_data["password"])
    user = User.objects.create(**validated_data)
    logger.info("op=create status=success user_id=%s", user.id)
    return user


class LoginSerialiser(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True)

  def validate(self, data):
    username = data.get("username")
    password = data.get("password")
    logger.info("op=validate username=%s", username)

    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      logger.warning("op=validate status=failed reason=user_not_found username=%s", username)
      raise serializers.ValidationError("Invalid username or password.")

    if not BCruptUtil.verify_password(password, user.password):
      logger.warning("op=validate status=failed reason=invalid_password username=%s", username)
      raise serializers.ValidationError("Invalid username or password.")

    logger.info("op=validate status=success user_id=%s username=%s", user.id, username)
    data["user"] = user
    return data

