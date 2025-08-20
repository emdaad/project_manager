from django.shortcuts import render
from rest_framework import viewsets, generics, status
from .models import User, Project, Task, Comment, membership
from .serializers import UserSerializer, RegisterSerializer, ProjectSerializer, TaskSerializer, CommentSerializer, MembershipSerializer
from .permissions import IsProjectOwnerOrAdmin, IsTaskAssignerOrReadOnly, IsAdminOrProjectOwnerForMembership, IsProjectMemberForTaskComments
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, VerifyOTPSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []  


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]





class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrAdmin] 
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
             raise PermissionDenied("only admins can create projects.")
        project = serializer.save(owner=self.request.user)
        project.members.add(self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update projects.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete projects.")
        instance.delete()            

class TaskFilter(FilterSet):
    due_date = DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ['status', 'priority', 'assignee']


class TaskViewSet(viewsets.ModelViewSet):
            queryset = Task.objects.all()
            serializer_class = TaskSerializer
            filter_backends = [DjangoFilterBackend]
            filterset_class = TaskFilter
            search_fields = ['title', 'description']
            ordering_fields = ['created_at', 'due_date', 'priority']

            def perform_create(self, serializer):
                project = serializer.validated_data.get('project')
                if not project:
                    raise PermissionDenied("Project is required for creating a task.")

                if not (self.request.user.is_staff or project.owner == self.request.user):
                    raise PermissionDenied("Only admins or the project owner can create tasks.")
        
                serializer.save()

            def perform_update(self, serializer):
                project = serializer.instance.project
                if not (self.request.user.is_staff or project.owner == self.request.user):
                    raise PermissionDenied("Only admins or the project owner can update tasks.")
                serializer.save()

            def perform_destroy(self, instance):
                project = instance.project
                if not (self.request.user.is_staff or project.owner == self.request.user):
                    raise PermissionDenied("Only admins or the project owner can delete tasks.")
                instance.delete()

class CommentViewSet(viewsets.ModelViewSet):
      queryset = Comment.objects.all()
      serializer_class = CommentSerializer
      permission_classes = [IsAuthenticated, IsProjectMemberForTaskComments]

      def perform_create(self, serializer):
           task = serializer.validated_data['task']
           project = task.project
           if not (self.request.user == project.owner or self.request.user in project.members.all()):
               raise PermissionDenied("You must be a member of the project to comment.")
           serializer.save(author=self.request.user)

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsAdminOrProjectOwnerForMembership]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
             raise PermissionDenied("Only admin can assign memberships.")
        serializer.save() 


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['username', 'password']
        ),
        responses={200: "OTP sent successfully"}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user returned after login'),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='One-Time Password sent to email/phone'),
            },
            required=['user_id', 'otp']
        ),
        responses={200: "JWT tokens returned"}
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(id=serializer.validated_data['user_id'])
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Your username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Your password'),
            },
            required=['username', 'password']
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)          