from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer


class LessonViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    class Meta:
        model = Lesson
