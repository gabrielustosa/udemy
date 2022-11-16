from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CourseViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    class Meta:
        model = Course
