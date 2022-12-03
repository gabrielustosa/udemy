from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from udemy.apps.course.models import Course


class IsInstructor(permissions.BasePermission):
    """Object permission to allow only course instructors."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'is_instructor'):
            return obj.is_instructor

        course = obj if isinstance(obj, Course) else obj.course
        is_instructor = course.instructors.filter(id=request.user.id).exists()
        return is_instructor


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow access to admin user or read only."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_staff
            or request.method in SAFE_METHODS
        )


class IsCreatorObject(permissions.BasePermission):
    """Allow access only for the creator of the object."""

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.creator == request.user
            or request.method in SAFE_METHODS
        )


class IsEnrolled(permissions.BasePermission):
    """Allow access only for enrolled students or course's instructors."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'is_enrolled') or hasattr(obj, 'is_instructor'):
            return obj.is_enrolled or obj.is_instructor

        course = obj if isinstance(obj, Course) else obj.course
        is_enrolled = request.user.enrolled_courses.filter(id=course.id).exists()
        is_instructor = course.instructors.filter(id=request.user.id).exists()
        return is_enrolled or is_instructor
