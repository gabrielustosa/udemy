from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, status

from udemy.apps.core.decorator import componentize
from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course, CourseRelation
from udemy.apps.course.serializer import CourseSerializer, CourseRelationSerializer


class CourseViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    class Meta:
        model = Course

    @componentize(result_name='details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @componentize()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CourseRelationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = CourseRelation.objects.all()
    serializer_class = CourseRelationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        query = CourseRelation.objects.filter(course=request.data['course'], creator=self.request.user)
        if query.exists():
            return Response({'course': 'You already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
