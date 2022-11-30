from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.action import QuestionActionFactory
from tests.factories.course import CourseFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.course.models import CourseRelation


def question_action_url(pk): return reverse('question:action-list', kwargs={'question_id': pk})


def question_action_url_detail(pk, action):
    return reverse('question:action-detail', kwargs={'question_id': pk, 'action': action})


class TestQuestionAction(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    @parameterized.expand([
        (1,),
        (2,)
    ])
    def test_send_action_to_question(self, action):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'action': action,
        }

        response = self.client.post(question_action_url(question.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(question.actions.filter(action=action).count(), 1)

    def test_action_question_list(self):
        question = QuestionFactory()
        CourseRelation.objects.create(course=question.course, creator=self.user)
        actions = QuestionActionFactory.create_batch(10, content_object=question)

        response = self.client.get(question_action_url(question.id))

        actions = ActionSerializer(actions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, actions.data)
        self.assertEqual(question.actions.count(), 10)

    def test_question_action_retrieve(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)
        action = QuestionActionFactory(content_object=question, action=1)

        response = self.client.get(question_action_url_detail(question.id, 1))

        serializer = ActionSerializer(action)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_question_action_delete(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)
        action = QuestionActionFactory(content_object=question, action=1)

        response = self.client.delete(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.objects.filter(id=action.id).exists())

    def test_user_cant_delete_action_that_is_not_his_own(self):
        other_user = UserFactory()
        question = QuestionFactory(creator=other_user)
        CourseRelation.objects.create(course=question.course, creator=self.user)
        QuestionActionFactory(content_object=question, action=1)

        response = self.client.get(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_question_action_retrieve_only_own_user_action(self):
        question = QuestionFactory()
        CourseRelation.objects.create(course=question.course, creator=self.user)
        QuestionActionFactory(content_object=question, action=1)

        response = self.client.get(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
