from rest_framework import mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer


class ActionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, raise_exception=True):
        filter_kwargs = {
            'content_type__model': self.request.data['content_object']['model'],
            'creator': self.request.user,
            'action': self.request.data['action'],
            'object_id': self.request.data['content_object']['object_id']
        }
        if raise_exception:
            obj = get_object_or_404(Action, **filter_kwargs)
        else:
            obj = Action.objects.filter(**filter_kwargs).first()
        return obj

    def create(self, request, *args, **kwargs):
        action = self.get_object(raise_exception=False)
        if action:
            return Response({'action': 'This action already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
