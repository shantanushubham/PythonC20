from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from users.serializers import LoginSerialzer, SignUpSerializer
from users.services import AuthService

# Create your views here.


class SignupAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = AuthService.signup(serializer.validated_data)
        return Response(token, status=HTTP_201_CREATED)


class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerialzer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = AuthService.login(serializer.validated_data["user"])
        return Response(token)
