from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from tests.factories.quiz import QuizFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.quiz.models import Quiz
from udemy.apps.quiz.serializer import QuizSerializer

QUIZ_LIST_URL = reverse('quiz:quiz-list')


def quiz_detail_url(pk): return reverse('quiz:quiz-detail', kwargs={'pk': pk})


class PublicQuizAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_quiz(self):
        response = self.client.post(QUIZ_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateQuizAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_quiz(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        course.instructors.add(self.user)

        payload = {
            'course': course.id,
            'module': module.id,
            'title': 'Test title',
            'description': 'Test content',
            'pass_percent': 50,
        }
        response = self.client.post(QUIZ_LIST_URL, payload)

        quiz = Quiz.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload['title'], quiz.title)
        self.assertEqual(payload['description'], quiz.description)
        self.assertEqual(payload['pass_percent'], quiz.pass_percent)

    def test_retrieve_quiz(self):
        quiz = QuizFactory()
        CourseRelation.objects.create(creator=self.user, course=quiz.course)

        response = self.client.get(quiz_detail_url(quiz.id))

        serializer = QuizSerializer(quiz)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_not_enrolled_can_retrieve_quiz(self):
        quiz = QuizFactory()

        response = self.client.get(quiz_detail_url(quiz.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_full_quiz_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        quiz = QuizFactory(course=course)

        payload = {
            'title': 'new title',
            'description': 'new content',
            'pass_percent': 90
        }
        response = self.client.put(quiz_detail_url(quiz.id), payload)

        quiz.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(quiz.title, payload['title'])
        self.assertEqual(quiz.description, payload['description'])

    def test_partial_quiz_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        quiz = QuizFactory(course=course)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(quiz_detail_url(pk=quiz.id), payload)

        quiz.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(quiz.title, payload['title'])

    def test_delete_quiz(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        quiz = QuizFactory(course=course)

        response = self.client.delete(quiz_detail_url(pk=quiz.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())

    def test_user_not_instructor_cant_create_quiz(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)

        payload = {
            'course': course.id,
            'module': module.id,
            'title': 'Test title',
            'description': 'Test content',
            'pass_percent': 50,
        }
        response = self.client.post(QUIZ_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
