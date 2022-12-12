from django.test import TestCase
from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer

RATING_LIST_URL = reverse('rating:rating-list')


def rating_detail_url(pk): return reverse('rating:rating-detail', kwargs={'pk': pk})


class TestRatingUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_rating_retrieve(self):
        rating = RatingFactory()

        response = self.client.get(rating_detail_url(pk=rating.id))

        serializer = RatingSerializer(rating)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_rating(self):
        response = self.client.post(RATING_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestRatingAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_rating_create(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Rating.objects.filter(id=response.data['id']).exists())

    def test_partial_rating_update(self):
        original_comment = 'original comment'
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, comment=original_comment, creator=self.user)

        payload = {
            'rating': 3,
        }
        response = self.client.patch(rating_detail_url(pk=rating.id), payload)

        rating.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating.rating, payload['rating'])
        self.assertEqual(rating.comment, original_comment)

    def test_rating_full_update(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)

        payload = {
            'rating': 3,
            'comment': 'new comment',
        }
        response = self.client.put(rating_detail_url(pk=rating.id), payload)

        rating.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating.rating, payload['rating'])
        self.assertEqual(rating.comment, payload['comment'])

    def test_delete_rating(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)

        response = self.client.delete(rating_detail_url(pk=rating.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rating.objects.filter(id=rating.id).exists())

