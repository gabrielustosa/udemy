from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.question.models import Question, Answer
from udemy.apps.question.serializer import QuestionSerializer, AnswerSerializer


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsEnrolled, IsCreatorObject, IsAuthenticatedOrReadOnly]


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsEnrolled, IsCreatorObject, IsAuthenticatedOrReadOnly]
