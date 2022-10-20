from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer
from utils.module import import_name


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def retrieve(self, request, *args, **kwargs):
        old_response = super().retrieve(request, args, kwargs)

        response = {
            'course_info': old_response.data,
        }

        components = request.query_params.get('components', None)
        if components:
            for component in components.split(','):
                function = import_name('udemy.apps.course.components', component)
                if not function:
                    continue
                response.update({
                    component: function()
                })

        return Response(response, status=old_response.status_code)
