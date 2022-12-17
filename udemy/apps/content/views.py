from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.content.models import Content
from udemy.apps.content.serializer import ContentSerializer
from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsInstructor, IsEnrolled


class ContentViewSet(
    view.ActionPermissionMixin,
    view.RelatedObjectViewMixin,
    view.AnnotatePermissionMixin,
    view.DynamicFieldViewMixin,
    ModelViewSet
):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled]
    }

    class Meta:
        model = Content
