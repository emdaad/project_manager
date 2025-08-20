from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied


class IsProjectOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if request.method in SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
       
        return request.user == obj.owner or request.user.is_staff

class IsTaskAssignerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        
        return request.user.is_staff or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.is_staff or obj.project.owner == request.user


class IsAdminOrProjectOwnerForMembership(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_staff or obj.project.owner == request.user
    

class IsProjectMemberForTaskComments(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        project = obj.task.project
        return (
            request.user == project.owner or
            request.user in project.members.all()
        )