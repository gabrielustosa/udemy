from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import ValidateOrderMixin
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.module.models import Module
from udemy.apps.module.serializer import ModuleSerializer


class ModuleViewSet(ValidateOrderMixin, ModelViewSet):
    queryset = Module.objects.select_related('course').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]
