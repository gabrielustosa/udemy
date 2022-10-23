from django.db.models import Max, PositiveIntegerField, F, ExpressionWrapper
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
            return Response({'detail': 'Order is automatically generated.'}, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        queryset = self.get_queryset().filter(course=serializer.validated_data['course'],
                                              module=serializer.validated_data['module'])
        course = serializer.validated_data['course']

        if queryset.exists():
            last_lesson = queryset.aggregate(last_order=Max('order'))['last_order']
            order = last_lesson + 1
        else:
            last_lesson = course.get_last_lesson_order()

            if last_lesson:
                order = last_lesson + 1
            else:
                order = 1

        serializer.validated_data['order'] = order

        course.lessons.filter(order__gte=order).update(
            order=ExpressionWrapper(F('order') + 1, output_field=PositiveIntegerField()))

        return super().perform_create(serializer)

    def update(self, request, *args, **kwargs):

        if 'order' in request.data:
            course = self.get_object().course
            last_order = course.get_last_lesson_order()
            new_order = int(request.data['order'])

            if new_order > last_order:
                return Response({'detail': 'The order can not be greater than last order of the lesson.'},
                                status.HTTP_400_BAD_REQUEST)

            current_order = self.get_object().order

            if current_order != new_order:
                number, query = (1, {'order__gte': new_order, 'order__lt': current_order}) if current_order > new_order \
                    else (-1, {'order__lte': new_order, 'order__gt': current_order})

                course.lessons.filter(**query).update(
                    order=ExpressionWrapper(F('order') + number, output_field=PositiveIntegerField()))

        return super().update(request, *args, **kwargs)
