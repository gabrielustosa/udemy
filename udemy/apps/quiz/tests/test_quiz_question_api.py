from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.quiz import QuizFactory, QuestionFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.quiz.models import Question
from udemy.apps.quiz.serializer import QuestionSerializer

QUIZ_QUESTION_LIST_URL = reverse('quiz:quiz-question-list', kwargs={'quiz_id': 0})


def quiz_question_detail_url(pk): return reverse('quiz:quiz-question-detail', kwargs={'pk': pk, 'quiz_id': 0})


class TestQuizQuestionUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_quiz(self):
        response = self.client.post(QUIZ_QUESTION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestQuizQuestionAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_quiz_question(self):
        course = CourseFactory()
        quiz = QuizFactory(course=course)
        course.instructors.add(self.user)

        payload = {
            'course': course.id,
            'quiz': quiz.id,
            'question': 'Test question',
            'feedback': 'Test feedback',
            'answers': [
                'answer 1',
                'answer 2',
                'answer 3',
            ],
            'correct_response': 3
        }
        response = self.client.post(QUIZ_QUESTION_LIST_URL, payload, format='json')

        question = Question.objects.get(id=response.data['id'])

        serializer = QuestionSerializer(question)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_quiz_question(self):
        question = QuestionFactory()
        CourseRelation.objects.create(creator=self.user, course=question.course)

        response = self.client.get(quiz_question_detail_url(question.id))

        serializer = QuestionSerializer(question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_full_quiz_question_update(self):
        question = QuestionFactory()
        question.course.instructors.add(self.user)

        payload = {
            'question': 'new question',
            'feedback': 'new feedback',
            'answers': [
                'new answer 1',
                'new answer 2',
                'new answer 3',
            ],
            'correct_response': 2
        }
        response = self.client.put(quiz_question_detail_url(question.id), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload['question'], question.question)
        self.assertEqual(payload['feedback'], question.feedback)
        self.assertEqual(payload['answers'], question.answers)

    def test_partial_quiz_question_update(self):
        question = QuestionFactory()
        question.course.instructors.add(self.user)

        payload = {
            'question': 'new question',
        }
        response = self.client.patch(quiz_question_detail_url(pk=question.id), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payload['question'], question.question)

    def test_delete_quiz_question(self):
        question = QuestionFactory()
        question.course.instructors.add(self.user)

        response = self.client.delete(quiz_question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())
