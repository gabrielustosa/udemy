from django.test import TestCase

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.answer import AnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.question import QuestionFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.question.models import Question, Answer
from udemy.apps.question.serializer import QuestionSerializer, AnswerSerializer

ANSWER_LIST_URL = reverse('answer-list')


def answer_detail_url(pk): return reverse('answer-detail', kwargs={'pk': pk})


class PublicAnswerAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_answer(self):
        response = self.client.post(ANSWER_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAnswerAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_answer(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        QuestionFactory()

        payload = {
            'course': 1,
            'question': 1,
            'content': 'content',
        }
        response = self.client.post(ANSWER_LIST_URL, payload)

        answer = Answer.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], answer.content)

    def test_partial_answer_update(self):
        answer = AnswerFactory(creator=self.user)
        CourseRelation.objects.create(course=answer.course, current_lesson=1, creator=self.user)

        payload = {
            'content': 'new content'
        }
        response = self.client.patch(answer_detail_url(pk=answer.id), payload)

        answer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.content, payload['content'])

    def test_delete_answer(self):
        answer = AnswerFactory(creator=self.user)
        CourseRelation.objects.create(course=answer.course, current_lesson=1, creator=self.user)

        response = self.client.delete(answer_detail_url(pk=answer.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Answer.objects.filter(id=answer.id).exists())

    def test_user_not_enrolled_can_answer(self):
        answer = AnswerFactory()

        response = self.client.delete(answer_detail_url(pk=answer.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_answer_content_greater_than_999(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'title',
            'content': ''.join(['a' for _ in range(1000)]),
            'lesson': 1,
            'course': 1
        }
        response = self.client.post(ANSWER_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
