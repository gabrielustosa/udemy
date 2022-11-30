from django.test import TestCase
from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.answer import RatingAnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation


def rating_answer_url(pk): return reverse('rating:answer-list', kwargs={'rating_id': pk})


class TestRatingAnswer(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_user_create_rating_answer(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'content': 'answer content'
        }

        response = self.client.post(rating_answer_url(rating.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rating.answers.count(), 1)

    def test_answer_rating_list(self):
        rating = RatingFactory(creator=self.user)
        CourseRelation.objects.create(course=rating.course, creator=self.user)

        answers = RatingAnswerFactory.create_batch(10, content_object=rating)

        response = self.client.get(rating_answer_url(rating.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
