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

from task_app.views import add_two_numbers, create_task, get_all_tasks, task_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add/', add_two_numbers),
    path('tasks/', get_all_tasks),
    path('tasks/create/', create_task),
    path('tasks/<uuid:task_id>/', task_detail),
]

# www.airtribe.live/add?a=10&b=20 -- here a and b are request parameter and the URL is "/add"
# www.airtribe.live/tasks/1 - here 1 is a path parameter and the URL is "/tasks/1"
