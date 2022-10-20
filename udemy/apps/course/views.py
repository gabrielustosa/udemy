from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.decorator import componentize
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @componentize(result_name='details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @componentize(result_name='list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
