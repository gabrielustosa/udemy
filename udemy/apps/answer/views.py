from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.answer.models import Answer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.question.models import Question
from udemy.apps.rating.models import Rating


class AnswerViewSetBase(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsEnrolled, IsCreatorObject]
    lookup_url_kwarg = 'answer_id'
    model = None
    pk_url_kwarg = None

    def get_filter_kwargs(self):
        filter_kwargs = {
            'content_type__model': self.model.__name__.lower(),
            'object_id': self.kwargs.get(self.pk_url_kwarg)
        }
        return filter_kwargs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['object_id'] = self.kwargs.get(self.pk_url_kwarg)
        context['model'] = self.model
        return context


class RatingAnswerViewSet(AnswerViewSetBase):
    model = Rating
    pk_url_kwarg = 'rating_id'

    def get_queryset(self):
        return self.queryset.filter(**self.get_filter_kwargs())


class QuestionAnswerViewSet(AnswerViewSetBase):
    model = Question
    pk_url_kwarg = 'question_id'

    def get_queryset(self):
        return self.queryset.filter(**self.get_filter_kwargs())
