"""
URL configuration for task_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from task_app.demo_views import (
    AsyncSyncToAsyncDemoView,
    AsyncTaskDemoView,
    SyncTaskDemoView,
)
from task_app.views import (
    TaskViewSet,
    UserViewSet,
    LoginView,
    SignUpView,
)


router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/signup/", SignUpView.as_view()),
    path("api/demo/sync-tasks/", SyncTaskDemoView.as_view()),
    path("api/demo/async-tasks/", AsyncTaskDemoView.as_view()),
    path("api/demo/sync-to-async/", AsyncSyncToAsyncDemoView.as_view()),
]

urlpatterns.extend(router.urls)

# www.airtribe.live/add?a=10&b=20 -- here a and b are request parameter and the URL is "/add"
# www.airtribe.live/tasks/1 - here 1 is a path parameter and the URL is "/tasks/1"
