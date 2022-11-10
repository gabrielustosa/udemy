from django.http import Http404

from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.action.models import Action
from udemy.apps.action.serializer import RatingActionSerializer, QuestionActionSerializer, AnswerActionSerializer
from udemy.apps.core.permissions import IsEnrolled


class ActionViewSetBase(ModelViewSet):
    queryset = Action.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsEnrolled]

    def get_object(self):
        filter_kwargs = {
            'creator': self.request.user,
            'content_type__model': self.model_name,
            'action': self.kwargs.get('action') or self.request.data['action'],
            'object_id': self.kwargs.get(self.pk_url_kwarg)
        }
        obj = get_object_or_404(Action, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        try:
            self.get_object()
            return Response({'action': 'This action already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            pass
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['object_id'] = self.kwargs.get(self.pk_url_kwarg)
        return context


class RatingActionViewSet(ActionViewSetBase):
    serializer_class = RatingActionSerializer
    model_name = 'rating'
    pk_url_kwarg = 'rating_id'


class QuestionActionViewSet(ActionViewSetBase):
    serializer_class = QuestionActionSerializer
    model_name = 'question'
    pk_url_kwarg = 'question_id'


class AnswerActionViewSet(ActionViewSetBase):
    serializer_class = AnswerActionSerializer
    model_name = 'answer'
    pk_url_kwarg = 'answer_id'
