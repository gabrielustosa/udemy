from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from udemy.apps.answer.models import Answer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject


class AnswerViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsEnrolled, IsCreatorObject, IsAuthenticatedOrReadOnly]

    def get_object(self):
        filter_kwargs = {
            'creator': self.request.user,
            'content_type__model': self.request.data['content_object']['model'],
            'object_id': self.request.data['content_object']['object_id']
        }
        obj = get_object_or_404(Answer, **filter_kwargs)
        return obj
