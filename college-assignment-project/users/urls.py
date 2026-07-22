from django.urls import path

from users.views import LoginAPIView, SignupAPIView


urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
]
