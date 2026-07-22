from rest_framework import serializers
from django.contrib.auth import authenticate

from academics.models import Department


class SignUpSerializer(serializers.Serializer):
    USER_TYPES = (("student", "Student"), ("teacher"), ("Teacher"))

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    user_type = serializers.ChoiceField(choices=USER_TYPES)

    # Student only
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False
    )

    roll_number = serializers.CharField(required=False)
    employee_id = serializers.CharField(required=False)

    def validate(self, attrs):
        user_type = attrs["user_type"]

        if user_type == "student":
            if not attrs.get("department"):
                raise serializers.ValidationError("Department is required.")

            if not attrs.get("roll_number"):
                raise serializers.ValidationError("Roll Number is required.")

        else:
            if not attrs.get("employee_id"):
                raise serializers.ValidationError("Employee ID is required.")

        return attrs


class LoginSerialzer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        user = authenticate(
            username=attrs["username"],
            password=attrs["password"]
        )

        if user is None:
            raise serializers.ValidationError("Invalid Credentials.")

        attrs["user"] = user

        return attrs
