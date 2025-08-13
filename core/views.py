from django.shortcuts import render
from rest_framework import viewsets, generics
from .models import User, Project, Task, Comment, membership
from .serializers import UserSerializer, RegisterSerializer, ProjectSerializer, TaskSerializer, CommentSerializer, MembershipSerializer
from .permissions import IsProjectOwnerOrAdmin, IsTaskAssignerOrReadOnly, IsAdminOrProjectOwnerForMembership, IsProjectMemberForTaskComments
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


# Create your views here.

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

class TaskViewSet(viewsets.ModelViewSet):
            queryset = Task.objects.all()
            serializer_class = TaskSerializer
            filterset_fields = ['status', 'priority', 'assignee']
            search_fields = ['title', 'description']
            ordering_fields = ['created_at', 'due_date', 'priority']
            permission_classes = [IsAuthenticated, IsTaskAssignerOrReadOnly]

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
           serializer.save(user=self.request.user)

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsAdminOrProjectOwnerForMembership]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
             raise PermissionDenied("Only admin can assign memberships.")
        serializer.save() 