from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.content.models import Content
from udemy.apps.content.serializer import ContentSerializer
from udemy.apps.core.mixins import ValidateOrderMixin, RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsInstructor


class ContentViewSet(RetrieveNestedObjectMixin, ValidateOrderMixin, ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]
