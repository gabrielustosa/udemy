from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsInstructor
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    def create(self, request, *args, **kwargs):
        if 'order' in request.data:
            return Response({'order': 'Order is automatically generated.'}, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        if 'order' in request.data:
            last_order = self.get_object().get_last_order()
            new_order = int(request.data['order'])

            if new_order > last_order:
                return Response({'order': 'The order can not be greater than last order of the module.'},
                                status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)
