from django.db import transaction
from rest_framework_simplejwt.tokens import AccessToken

from academics.models import Student, Teacher
from users.models import User


class AuthService:

    @staticmethod
    @transaction.atomic
    def signup(validated_data):
        user_type = validated_data.pop("user_type")
        department = validated_data.pop("department", None)
        roll_number = validated_data.pop("roll_number", None)

        password = validated_data.pop("password")
        employee_id = validated_data.pop("employee_id")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user_type == "student":
            Student.objects.create(
                user=user, department=department, roll_number=roll_number
            )
        else:
            Teacher.objects.create(user=user, employee_id=employee_id)

        token = AccessToken.for_user(user)

        return {"access": str(token)}

    @staticmethod
    def login(user):

        token = AccessToken.for_user(user)

        return {"access": str(token)}
