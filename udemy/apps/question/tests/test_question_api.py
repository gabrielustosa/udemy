from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer

QUESTION_LIST_URL = reverse('question:question-list')


def question_detail_url(pk): return reverse('question:question-detail', kwargs={'pk': pk})


class TestQuestionAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_question(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'title': 'title',
            'content': 'content',
            'lesson': lesson.id,
            'course': course.id
        }
        response = self.client.post(QUESTION_LIST_URL, payload)

        question = Question.objects.get(id=response.data['id'])

        serializer = QuestionSerializer(question)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_module_retrieve(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)

        response = self.client.get(question_detail_url(question.id))

        serializer = QuestionSerializer(question)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_question_update(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(question_detail_url(question.id), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question.title, payload['title'])

    def test_full_question_update(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)

        payload = {
            'title': 'new title',
            'content': 'new content'
        }
        response = self.client.put(question_detail_url(question.id), payload)

        question.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question.title, payload['title'])
        self.assertEqual(question.content, payload['content'])

    def test_delete_question(self):
        question = QuestionFactory(creator=self.user)
        CourseRelation.objects.create(course=question.course, creator=self.user)

        response = self.client.delete(question_detail_url(pk=question.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=question.id).exists())
