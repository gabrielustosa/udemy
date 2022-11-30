from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.answer.models import Answer
from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.question.models import Question
from udemy.apps.rating.models import Rating


class ActionViewSetBase(
    view.AnnotatePermissionMixin,
    view.RetrieveRelatedObjectMixin,
    ModelViewSet
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated, IsEnrolled]

    class Meta:
        model = Action

    def get_filter_kwargs(self):
        action = self.kwargs.get('action') or self.request.data.get('action')

        filter_kwargs = {
            'content_type__model': self.model.__name__.lower(),
            'object_id': self.kwargs.get(self.pk_url_kwarg)
        }
        if action:
            filter_kwargs.update({'action': action})

        return filter_kwargs

    def get_object(self):
        filter_kwargs = {
            **self.get_filter_kwargs(),
            'creator': self.request.user,
        }
        obj = get_object_or_404(Action, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        return self.queryset.filter(**self.get_filter_kwargs())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['object_id'] = self.kwargs.get(self.pk_url_kwarg)
        context['model'] = self.model
        return context


class RatingActionViewSet(view.ActionPermissionMixin, ActionViewSetBase):
    model = Rating
    pk_url_kwarg = 'rating_id'
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsEnrolled],
        ('retrieve', 'list'): [AllowAny],
    }


class QuestionActionViewSet(ActionViewSetBase):
    model = Question
    pk_url_kwarg = 'question_id'


class AnswerActionViewSet(ActionViewSetBase):
    model = Answer
    pk_url_kwarg = 'answer_id'
