from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsEnrolled, IsCreatorObject, IsAuthenticatedOrReadOnly]
