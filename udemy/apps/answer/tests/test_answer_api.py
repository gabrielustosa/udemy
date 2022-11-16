from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.answer import AnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.answer.models import Answer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation


def answer_detail_url(pk): return reverse('answer:detail', kwargs={'answer_id': pk})


class PublicAnswerTestAPI(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_action(self):
        response = self.client.post(answer_detail_url(1))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_answer_retrieve(self):
        answer = AnswerFactory()

        response = self.client.get(answer_detail_url(1))

        serializer = AnswerSerializer(answer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_answer_delete_if_user_is_not_enrolled(self):
        AnswerFactory()

        response = self.client.delete(answer_detail_url(1))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_delete_if_user_is_not_the_creator(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        AnswerFactory(course=course)

        response = self.client.delete(answer_detail_url(1))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_delete(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        AnswerFactory(course=course, creator=self.user)

        response = self.client.delete(answer_detail_url(1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Answer.objects.filter(id=1).exists())

    def test_answer_patch(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        answer = AnswerFactory(course=course, creator=self.user)

        payload = {
            'content': 'new content'
        }

        response = self.client.patch(answer_detail_url(1), payload)

        answer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.content, payload['content'])
