from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CourseViewSet(
    view.AnnotatePermissionMixin,
    view.ActionPermissionMixin,
    view.RetrieveRelatedObjectMixin,
    view.DynamicFieldViewMixin,
    view.AnnotateMethodsMixin,
    ModelViewSet
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('create',): [IsAuthenticated],
        ('retrieve', 'list'): [AllowAny],
    }

    class Meta:
        model = Course
