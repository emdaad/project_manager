from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProjectViewSet, TaskViewSet, LoginView, CommentViewSet, UserViewSet, MembershipViewSet, VerifyOTPView


router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'users', UserViewSet, basename='users')
router.register(r'memberships', MembershipViewSet, basename='memberships')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('auth/login/', LoginView.as_view(), name='two_factor_login'),  
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),       
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls