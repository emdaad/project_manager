from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from .views import ProjectViewSet, TaskViewSet, CommentViewSet, UserViewSet, MembershipViewSet

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'users', UserViewSet, basename='users')
router.register(r'memberships', MembershipViewSet, basename='memberships')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
] + router.urls