from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.answer import MessageAnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.message import MessageFactory
from tests.factories.user import UserFactory

from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation


def message_answer_url(pk): return reverse('message:answer-list', kwargs={'message_id': pk})


class TestMessageAnswer(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_can_answer_message(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        message = MessageFactory(course=course)

        payload = {
            'course': course.id,
            'content': 'answer content'
        }

        response = self.client.post(message_answer_url(message.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(message.answers.count(), 1)

    def test_answers_message_list(self):
        message = MessageFactory()
        CourseRelation.objects.create(course=message.course, creator=self.user)

        answers = MessageAnswerFactory.create_batch(10, content_object=message)

        response = self.client.get(message_answer_url(message.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
