from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer


class QuestionViewSet(
    view.AnnotatePermissionMixin,
    view.RelatedObjectViewMixin,
    view.DynamicFieldViewMixin,
    ModelViewSet
):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsEnrolled, IsCreatorObject]

    class Meta:
        model = Question
