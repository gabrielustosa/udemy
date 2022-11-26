from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from udemy.apps.action.serializer import ActionSerializer

from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.user.serializer import UserSerializer


def question_action_url(pk): return reverse('question:action-list', kwargs={'question_id': pk})


def question_action_url_detail(pk, action):
    return reverse('question:action-detail', kwargs={'question_id': pk, 'action': action})


class PublicActionTestAPI(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_action(self):
        question = QuestionFactory()

        response = self.client.post(question_action_url(question.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_cant_create_same_action_twice(self):
        question = QuestionFactory()
        course = question.course
        CourseRelation.objects.create(course=course, creator=self.user)
        ActionFactory(creator=self.user, course=course, content_object=question)

        payload = {
            'course': course.id,
            'action': 1,
        }

        with transaction.atomic():
            response = self.client.post(question_action_url(question.id), payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(question.actions.filter(action=1).count(), 1)

    def test_user_not_enrolled_can_create_action(self):
        question = QuestionFactory()
        course = question.course
        ActionFactory(creator=self.user, course=course, content_object=question)

        payload = {
            'course': course.id,
            'action': 1,
        }

        response = self.client.post(question_action_url(question.id), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        ('creator', ('id', 'name'), UserSerializer),
        ('course', ('id', 'title'), CourseSerializer),
    ])
    def test_related_objects(self, field_name, fields, Serializer):
        question = QuestionFactory()
        course = question.course
        CourseRelation.objects.create(course=course, creator=self.user)
        action = ActionFactory(creator=self.user, course=course, content_object=question)

        response = self.client.get(
            f'{question_action_url_detail(question.id, 1)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        action_serializer = ActionSerializer(action, fields=('@min',))
        object_serializer = Serializer(getattr(action, field_name), fields=fields)

        expected_response = {
            **action_serializer.data,
            field_name: {
                **object_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)
