from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.answer import QuestionAnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory

from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation


def question_answer_url(pk): return reverse('question:answer-list', kwargs={'question_id': pk})


class TestQuestionAnswer(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_create_question_answer(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        question = QuestionFactory(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'content': 'answer content'
        }

        response = self.client.post(question_answer_url(question.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(question.answers.count(), 1)

    def test_answer_question_list(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)

        answers = QuestionAnswerFactory.create_batch(10, content_object=question)

        response = self.client.get(question_answer_url(question.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
