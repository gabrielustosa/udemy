from django.test import TestCase

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.question import QuestionFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer

QUESTION_LIST_URL = reverse('question-list')


def question_detail_url(pk): return reverse('question-detail', kwargs={'pk': pk})


class PublicQuestionAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_question_list(self):
        categories = create_factory_in_batch(QuestionFactory, 5)

        response = self.client.get(QUESTION_LIST_URL)

        serializer = QuestionSerializer(categories, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_question(self):
        response = self.client.post(QUESTION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateQuestionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_question(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'title',
            'content': 'content',
            'lesson': 1,
            'course': 1
        }
        response = self.client.post(QUESTION_LIST_URL, payload)

        question = Question.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], question.title)

    def test_partial_question_update(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'new title',
            'content': 'new content'
        }
        response = self.client.patch(question_detail_url(pk=1), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question.title, payload['title'])
        self.assertEqual(question.content, payload['content'])

    def test_delete_question(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, current_lesson=1, creator=self.user)

        response = self.client.delete(question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())

    def test_user_not_enrolled_can_ask_a_question(self):
        question = QuestionFactory()

        response = self.client.delete(question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
