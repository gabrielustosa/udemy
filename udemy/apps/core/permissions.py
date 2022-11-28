from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from udemy.apps.course.models import Course, CourseRelation


class IsInstructor(permissions.BasePermission):
    """Object permission to allow only course instructors."""

    def has_object_permission(self, request, view, obj):
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
        course = obj if isinstance(obj, Course) else obj.course
        is_enrolled = CourseRelation.objects.filter(course=course, creator=request.user).exists()
        is_instructor = False
        if not is_enrolled:
            is_instructor = course.instructors.filter(id=request.user.id).exists()
        return is_enrolled or is_instructor
