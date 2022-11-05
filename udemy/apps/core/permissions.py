from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from udemy.apps.course.models import Course, CourseRelation


class IsInstructor(permissions.BasePermission):
    """Object permission to allow only course instructors to modify them courses."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        course = obj if isinstance(obj, Course) else obj.course
        is_instructor = course.instructors.filter(id=request.user.id).exists()
        return is_instructor

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        course_id = request.data.get('course')
        if not course_id:
            return True

        course = Course.objects.filter(id=course_id).first()
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
    """Allow access only for students enrolled in course."""

    def has_object_permission(self, request, view, obj):
        is_enrolled = CourseRelation.objects.filter(course=obj.course, creator=request.user).exists()
        return bool(
            is_enrolled or request.method in SAFE_METHODS
        )

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        course_id = request.data.get('course')
        if not course_id:
            return True

        is_enrolled = CourseRelation.objects.filter(course__id=course_id, creator=request.user).exists()
        return is_enrolled
