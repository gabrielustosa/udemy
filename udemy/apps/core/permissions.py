from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsInstructor(permissions.BasePermission):
    """Object permission to allow only course instructors to modify them courses."""

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.instructors.filter(id=request.user.id).exists()
            or request.method in SAFE_METHODS
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow access to admin user or read only for non-authenticated."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)
