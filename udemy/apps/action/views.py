from rest_framework import mixins, status
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

    def get_object(self):
        model = self.request.data['content_object']['model']
        object_id = self.request.data['content_object']['object_id']

        action = Action.objects.filter(
            content_type__model=model,
            creator=self.request.user,
            action=self.request.data['action'],
            object_id=object_id
        ).first()

        return action

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = self.get_object()
        if action:
            return Response({'action': 'This action already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.save()
        action.content_object.action.add(action)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = self.get_object()
        if not action:
            return Response({'action': 'Object not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(action)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = self.get_object()
        if not action:
            return Response({'action': 'Object not found.'}, status=status.HTTP_404_NOT_FOUND)

        action.content_object.action.remove(action)
        action.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
