from django.test import TestCase
from parameterized import parameterized

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.factories.answer import AnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.question import QuestionFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation
from udemy.apps.question.models import Question

QUESTION_LIST_URL = reverse('question:list')


def question_detail_url(pk): return reverse('question:detail', kwargs={'pk': pk})


def question_action_url(pk): return reverse('question:action-list', kwargs={'question_id': pk})


def question_action_url_detail(pk, action):
    return reverse('question:action-detail', kwargs={'question_id': pk, 'action': action})


def question_answer_url(pk): return reverse('question:answer-list', kwargs={'question_id': pk})


class PublicQuestionAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_question(self):
        response = self.client.post(QUESTION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateQuestionApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_question(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'title',
            'content': 'content',
            'lesson': 1,
            'course': 1
        }
        response = self.client.post(QUESTION_LIST_URL, payload)

        question = Question.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], question.title)

    def test_partial_question_update(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'new title',
            'content': 'new content'
        }
        response = self.client.patch(question_detail_url(pk=1), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question.title, payload['title'])
        self.assertEqual(question.content, payload['content'])

    def test_delete_question(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, current_lesson=1, creator=self.user)

        response = self.client.delete(question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())

    def test_user_not_enrolled_can_ask_a_question(self):
        question = QuestionFactory()

        response = self.client.delete(question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_question_title_less_than_5(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)

        payload = {
            'title': 't',
            'content': 'content',
            'lesson': 1,
            'course': 1
        }
        response = self.client.post(QUESTION_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_content_greater_than_100(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)

        payload = {
            'title': 'title',
            'content': ''.join(['a' for _ in range(1001)]),
            'lesson': 1,
            'course': 1
        }
        response = self.client.post(QUESTION_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand([
        (1,),
        (2,)
    ])
    def test_send_action_to_question(self, action):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)

        payload = {
            'course': 1,
            'action': action,
        }

        response = self.client.post(question_action_url(1), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(question.actions.filter(action=action).count(), 1)

    def test_action_question_list(self):
        question = QuestionFactory()
        actions = create_factory_in_batch(ActionFactory, 10, content_object=question)

        response = self.client.get(question_action_url(1))

        actions = ActionSerializer(actions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, actions.data)
        self.assertEqual(question.actions.count(), 10)

    def test_question_action_retrieve(self):
        question = QuestionFactory(creator=self.user)
        action = ActionFactory(creator=self.user, content_object=question)

        response = self.client.get(question_action_url_detail(question.id, 1))

        serializer = ActionSerializer(action)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_question_action_retrieve_only_own_user_action(self):
        question = QuestionFactory()
        ActionFactory(content_object=question)

        response = self.client.get(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_question_action_delete(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)
        ActionFactory(creator=self.user, content_object=question, course=course)

        response = self.client.delete(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.objects.filter(id=1).exists())

    def test_user_cant_delete_action_that_is_not_his(self):
        other_user = UserFactory()
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        question = QuestionFactory(course=course, creator=other_user)
        ActionFactory(content_object=question, course=course, creator=other_user)

        response = self.client.get(question_action_url_detail(question.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_create_question_answer(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)

        payload = {
            'course': 1,
            'content': 'answer content'
        }

        response = self.client.post(question_answer_url(question.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(question.answers.count(), 1)

    def test_answer_question_list(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)

        answers = create_factory_in_batch(AnswerFactory, 10, content_object=question, course=course)

        response = self.client.get(question_answer_url(question.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
