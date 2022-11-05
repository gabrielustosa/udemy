from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status

from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.factories.answer import AnswerFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory
from tests.utils import create_factory_in_batch
from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.question.models import Question

ACTION_LIST_URL = reverse('action:list')


class PublicActionTestAPI(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_action(self):
        response = self.client.post(ACTION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    @parameterized.expand([
        (1, QuestionFactory, 'question'),
        (2, QuestionFactory, 'question'),
        (1, AnswerFactory, 'answer'),
        (2, AnswerFactory, 'answer'),
        (1, RatingFactory, 'rating'),
        (2, RatingFactory, 'rating'),
    ])
    def test_create_action(self, action, Factory, model):
        factory = Factory()
        payload = {
            'action': action,
            'content_object': {
                'model': model,
                'object_id': 1
            }
        }

        response = self.client.post(ACTION_LIST_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(factory.action.filter(action=action).count(), 1)

    def test_user_cant_create_same_action_twice(self):
        ActionFactory(creator=self.user)

        payload = {
            'action': 1,
            'content_object': {
                'model': 'question',
                'object_id': 1
            }
        }

        response = self.client.post(ACTION_LIST_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.objects.first().action.filter(action=1).count(), 1)

    def test_action_correctly_working(self):
        question = QuestionFactory()
        create_factory_in_batch(ActionFactory, 12, action=1, content_object=question)
        create_factory_in_batch(ActionFactory, 9, action=2, content_object=question)

        self.assertEqual(question.action.filter(action=1).count(), 12)
        self.assertEqual(question.action.filter(action=2).count(), 9)

    def test_action_retrieve(self):
        action = ActionFactory(creator=self.user)

        payload = {
            'action': 1,
            'content_object': {
                'model': 'question',
                'object_id': 1
            }
        }

        data, content_type = self.client._encode_data(payload, 'json')
        response = self.client.generic('get', ACTION_LIST_URL, data, content_type)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ActionSerializer(action)
        self.assertEqual(response.data, serializer.data)

    def test_action_delete(self):
        ActionFactory(creator=self.user)

        payload = {
            'action': 1,
            'content_object': {
                'model': 'question',
                'object_id': 1
            }
        }

        response = self.client.delete(ACTION_LIST_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Action.objects.first())
