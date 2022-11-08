from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.question.models import Question


def question_action_url(pk): return reverse('question:action-list', kwargs={'question_id': pk})


class PublicActionTestAPI(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_action(self):
        response = self.client.post(question_action_url(1))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_cant_create_same_action_twice(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        ActionFactory(creator=self.user, course=course)

        payload = {
            'course': 1,
            'action': 1,
        }

        response = self.client.post(question_action_url(1), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.objects.first().actions.filter(action=1).count(), 1)