from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsInstructor, IsEnrolled
from udemy.apps.message.models import Message
from udemy.apps.message.serializer import MessageSerializer


class MessageViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsEnrolled, IsInstructor, IsAuthenticatedOrReadOnly]

    class Meta:
        model = Message
