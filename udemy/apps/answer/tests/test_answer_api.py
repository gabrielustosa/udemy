from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.answer import RatingAnswerFactory
from tests.factories.user import UserFactory
from udemy.apps.answer.models import Answer

from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation


def answer_detail_url(pk): return reverse('answer:detail', kwargs={'answer_id': pk})


class TestAnswerAPIRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_answer_retrieve(self):
        answer = RatingAnswerFactory()
        CourseRelation.objects.create(course=answer.course, creator=self.user)

        response = self.client.get(answer_detail_url(answer.id))

        serializer = AnswerSerializer(answer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_partial_answer_update(self):
        answer = RatingAnswerFactory(creator=self.user)
        CourseRelation.objects.create(course=answer.course, creator=self.user)

        payload = {
            'content': 'new content'
        }
        response = self.client.patch(answer_detail_url(answer.id), payload)

        answer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.content, payload['content'])

    def test_full_answer_update(self):
        answer = RatingAnswerFactory(creator=self.user)
        CourseRelation.objects.create(course=answer.course, creator=self.user)

        payload = {
            'content': 'new content'
        }
        response = self.client.put(answer_detail_url(answer.id), payload)

        answer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_answer_delete(self):
        answer = RatingAnswerFactory(creator=self.user)
        CourseRelation.objects.create(course=answer.course, creator=self.user)

        response = self.client.delete(answer_detail_url(answer.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Answer.objects.filter(id=answer.id).exists())
