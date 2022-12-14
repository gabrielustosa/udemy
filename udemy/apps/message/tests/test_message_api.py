from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.message import MessageFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.message.models import Message
from udemy.apps.message.serializer import MessageSerializer

MESSAGE_LIST_URL = reverse('message:message-list')


def message_detail_url(pk): return reverse('message:message-detail', kwargs={'pk': pk})


class TestMessageAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_message(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        payload = {
            'course': course.id,
            'title': 'Test title',
            'content': 'Test content',
        }
        response = self.client.post(MESSAGE_LIST_URL, payload)

        message = Message.objects.get(id=response.data['id'])

        serializer = MessageSerializer(message)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_message(self):
        message = MessageFactory()
        CourseRelation.objects.create(creator=self.user, course=message.course)

        response = self.client.get(message_detail_url(message.id))

        serializer = MessageSerializer(message)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_full_message_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        message = MessageFactory(course=course)

        payload = {
            'title': 'new title',
            'content': 'new content',
        }
        response = self.client.put(message_detail_url(message.id), payload)

        message.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(message.title, payload['title'])
        self.assertEqual(message.content, payload['content'])

    def test_partial_message_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        message = MessageFactory(course=course)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(message_detail_url(pk=message.id), payload)

        message.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(message.title, payload['title'])

    def test_delete_message(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        message = MessageFactory(course=course)

        response = self.client.delete(message_detail_url(pk=message.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(id=message.id).exists())


