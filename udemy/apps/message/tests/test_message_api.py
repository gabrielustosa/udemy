from django.test import TestCase
from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.answer import AnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.message import MessageFactory
from tests.factories.user import UserFactory
from tests.utils import create_factory_in_batch

from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.message.models import Message
from udemy.apps.message.serializer import MessageSerializer
from udemy.apps.user.serializer import UserSerializer

MESSAGE_LIST_URL = reverse('message:message-list')


def message_detail_url(pk): return reverse('message:message-detail', kwargs={'pk': pk})


def message_answer_url(pk): return reverse('message:answer-list', kwargs={'message_id': pk})


class PublicMessageAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_message(self):
        response = self.client.post(MESSAGE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMessageAPITests(TestCase):
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

        message = Message.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload['title'], message.title)
        self.assertEqual(payload['content'], message.content)

    def test_retrieve_message(self):
        message = MessageFactory()
        CourseRelation.objects.create(creator=self.user, course=message.course)

        response = self.client.get(message_detail_url(message.id))

        serializer = MessageSerializer(message)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_not_enrolled_can_retrieve_message(self):
        message = MessageFactory()

        response = self.client.get(message_detail_url(message.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_user_not_instructor_cant_create_message(self):
        course = CourseFactory()

        payload = {
            'course': course.id,
            'title': 'Test title',
            'content': 'Test content',
        }
        response = self.client.post(MESSAGE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        message = MessageFactory(course=course)

        answers = create_factory_in_batch(AnswerFactory, 10, content_object=message, course=course)

        response = self.client.get(message_answer_url(message.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @parameterized.expand([
        ('creator', ('id', 'name'), UserSerializer),
        ('course', ('id', 'title'), CourseSerializer),
    ])
    def test_related_objects(self, field_name, fields, Serializer):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        message = MessageFactory(course=course)

        response = self.client.get(
            f'{message_detail_url(message.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        message_serializer = MessageSerializer(message, fields=('@min',))
        object_serializer = Serializer(getattr(message, field_name), fields=fields)

        expected_response = {
            **message_serializer.data,
            field_name: {
                **object_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)
