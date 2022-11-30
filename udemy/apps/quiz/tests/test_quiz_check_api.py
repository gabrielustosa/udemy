from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.quiz import QuestionFactory, QuizFactory
from tests.factories.user import UserFactory

from udemy.apps.quiz.models import QuizRelation


def check_quiz_url(pk): return reverse('quiz:check', kwargs={'quiz_id': pk})


class TestQuizUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_check_quiz(self):
        response = self.client.post(check_quiz_url(1))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestQuizAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_not_enrolled_cant_check_quiz(self):
        quiz = QuizFactory()

        response = self.client.post(check_quiz_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_not_check_test_if_already_done(self):
        quiz = QuizFactory()
        QuizRelation.objects.create(quiz=quiz, creator=self.user, done=True)

        response = self.client.post(check_quiz_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_a_incorrect_numbers_of_responses(self):
        quiz = QuizFactory()
        QuizRelation.objects.create(quiz=quiz, creator=self.user)

        QuestionFactory.create_batch(5, quiz=quiz)

        payload = {
            'responses': [n for n in range(10)]
        }

        response = self.client.post(check_quiz_url(quiz.id), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_quiz_with_correct_responses(self):
        quiz = QuizFactory()
        QuizRelation.objects.create(quiz=quiz, creator=self.user)

        correct_responses = [3, 4, 5, 1, 2]

        [QuestionFactory(quiz=quiz, correct_response=correct) for correct in correct_responses]

        payload = {
            'responses': correct_responses
        }

        response = self.client.post(check_quiz_url(quiz.id), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['correct'])
        self.assertEqual(response.data['wrong_questions'], {})

    def test_check_quiz_with_wrong_responses(self):
        quiz = QuizFactory(pass_percent=50)
        QuizRelation.objects.create(quiz=quiz, creator=self.user)

        correct_responses = [3, 4, 5, 1, 2]

        [QuestionFactory(quiz=quiz, correct_response=correct) for correct in correct_responses]

        payload = {
            'responses': [2, 4, 5, 5, 1]
        }

        response = self.client.post(check_quiz_url(quiz.id), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['correct'])
        self.assertEqual(response.data['wrong_questions'], {
            1: 2,
            4: 5,
            5: 1
        })
