from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.decorator import componentize
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    @componentize(result_name='details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @componentize(result_name='list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
