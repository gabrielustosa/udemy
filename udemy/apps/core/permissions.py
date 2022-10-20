from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsInstructor(permissions.BasePermission):
    """Object permission to allow only course instructors to modify them courses."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.instructors.filter(id=request.user.id).exists()
