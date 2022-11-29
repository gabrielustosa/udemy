from django.db.models import Exists, OuterRef

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveRelatedObjectMixin, ActionPermissionMixin
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CourseViewSet(ActionPermissionMixin, RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('create',): [IsAuthenticated],
        ('retrieve', 'list'): [AllowAny],
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(is_enrolled=Exists(
                self.request.user.enrolled_courses.filter(id=OuterRef('id'))
            )).annotate(is_instructor=Exists(
                self.request.user.instructors_courses.filter(id=OuterRef('id'))
            ))

        return queryset

    class Meta:
        model = Course
