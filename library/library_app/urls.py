from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookIssueView, BookReturnView, BookViewSet, LoginView, MeView, SignUpView

router = DefaultRouter()
router.register('books', BookViewSet, basename='book')

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('issues/', BookIssueView.as_view(), name='book-issue'),
    path('issues/<int:pk>/return/', BookReturnView.as_view(), name='book-return'),
    path('', include(router.urls)),
]
