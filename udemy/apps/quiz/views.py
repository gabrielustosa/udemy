from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import view
from udemy.apps.core.permissions import IsInstructor, IsEnrolled
from udemy.apps.quiz.models import Quiz, Question, QuizRelation
from udemy.apps.quiz.serializer import QuizSerializer, QuestionSerializer


class QuizViewSet(
    view.ActionPermissionMixin,
    view.RelatedObjectViewMixin,
    view.AnnotatePermissionMixin,
    view.DynamicFieldViewMixin,
    view.AnnotationViewMixin,
    ModelViewSet
):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled],
    }

class QuestionViewSet(
    view.ActionPermissionMixin,
    view.RelatedObjectViewMixin,
    view.AnnotatePermissionMixin,
    ModelViewSet
):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsInstructor],
        ('retrieve', 'list'): [IsAuthenticated, IsEnrolled],
    }


class CheckQuizView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'quiz_id'

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=kwargs.get('quiz_id'))

        relation = QuizRelation.objects.filter(creator=request.user, quiz=quiz).first()

        if relation is None:
            return Response({'You are not enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)

        if relation.done:
            return Response({'You already completed this quiz.'}, status=status.HTTP_400_BAD_REQUEST)

        quiz_responses = quiz.questions.values_list('correct_response', flat=True)
        responses = request.data['responses']

        if len(responses) != len(quiz_responses):
            return Response({'The count of responses are incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        total = 0
        wrong_questions = dict()
        for index, response in enumerate(responses, start=1):
            if response == quiz_responses[index - 1]:
                total += 1
            else:
                wrong_questions[index] = response

        correct = (total * 100) / len(quiz_responses) >= quiz.pass_percent

        if correct:
            relation.done = True
            relation.save()

        return Response({
            'correct': correct,
            'wrong_questions': wrong_questions
        })
