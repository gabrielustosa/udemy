from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsInstructor, IsEnrolled
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer


class LessonViewSet(
    view.ActionPermissionMixin,
    view.RetrieveRelatedObjectMixin,
    view.AnnotatePermissionMixin,
    view.DynamicFieldViewMixin,
    ModelViewSet
):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled]
    }

    class Meta:
        model = Lesson
