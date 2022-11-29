from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core import mixins
from udemy.apps.core.permissions import IsInstructor, IsEnrolled
from udemy.apps.module.models import Module
from udemy.apps.module.serializer import ModuleSerializer


class ModuleViewSet(
    mixins.ActionPermissionMixin,
    mixins.RetrieveRelatedObjectMixin,
    mixins.AnnotatePermissionMixin,
    ModelViewSet
):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled]
    }

    class Meta:
        model = Module
