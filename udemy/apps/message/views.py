from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core import mixins
from udemy.apps.core.permissions import IsInstructor, IsEnrolled
from udemy.apps.message.models import Message
from udemy.apps.message.serializer import MessageSerializer


class MessageViewSet(
    mixins.ActionPermissionMixin,
    mixins.RetrieveRelatedObjectMixin,
    mixins.AnnotateIsEnrolledPermissionMixin,
    mixins.AnnotateIsInstructorPermissionMixin,
    ModelViewSet
):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled]
    }

    class Meta:
        model = Message
