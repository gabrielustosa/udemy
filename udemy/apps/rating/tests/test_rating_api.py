from django.test import TestCase
from django.shortcuts import reverse

from parameterized import parameterized

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.utils import create_factory_in_batch
from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.course.models import CourseRelation
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer

RATING_LIST_URL = reverse('rating:list')


def rating_detail_url(pk): return reverse('rating:detail', kwargs={'pk': pk})


def rating_action_url(pk): return reverse('rating:action-list', kwargs={'rating_id': pk})


def rating_action_url_detail(pk, action): return reverse('rating:action-detail',
                                                         kwargs={'rating_id': pk, 'action': action})


class PublicRatingAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_rating_list(self):
        ratings = create_factory_in_batch(RatingFactory, 5)

        response = self.client.get(RATING_LIST_URL)

        serializer = RatingSerializer(ratings, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rating_retrieve(self):
        rating = RatingFactory()

        response = self.client.get(rating_detail_url(pk=1))

        serializer = RatingSerializer(rating)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_rating(self):
        response = self.client.post(RATING_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRatingApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_rating_create(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cant_rating_course_twice(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        RatingFactory(creator=self.user, course=course)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_rate_a_course_not_enrolled(self):
        course = CourseFactory()

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        (0,),
        (6,)
    ])
    def test_user_cant_create_a_rating_with_rate_greater_than_5_less_than_1(self, rating):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

        payload = {
            'course': course.id,
            'rating': rating,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_rating_update(self):
        original_comment = 'original comment'
        rating = RatingFactory(comment=original_comment, creator=self.user)
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

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
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        rating = RatingFactory(creator=self.user)

        payload = {
            'course': 1,
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
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        rating = RatingFactory(creator=self.user)

        response = self.client.delete(rating_detail_url(pk=rating.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rating.objects.filter(id=rating.id).exists())

    @parameterized.expand([
        (1,),
        (2,)
    ])
    def test_send_action_to_question(self, action):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)

        payload = {
            'course': 1,
            'action': action,
        }

        response = self.client.post(rating_action_url(1), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rating.actions.filter(action=action).count(), 1)

    def test_action_question_list(self):
        rating = RatingFactory()
        actions = create_factory_in_batch(ActionFactory, 10, content_object=rating)

        response = self.client.get(rating_action_url(1))

        actions = ActionSerializer(actions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, actions.data)
        self.assertEqual(rating.actions.count(), 10)

    def test_question_action_retrieve(self):
        rating = RatingFactory(creator=self.user)
        action = ActionFactory(creator=self.user, content_object=rating)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        serializer = ActionSerializer(action)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_question_action_retrieve_only_own_user_action(self):
        rating = RatingFactory()
        ActionFactory(content_object=rating)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_question_action_delete(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)
        ActionFactory(creator=self.user, content_object=rating, course=course)

        response = self.client.delete(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.objects.filter(id=1).exists())

    def test_user_cant_delete_action_that_is_not_his(self):
        other_user = UserFactory()
        course = CourseFactory()
        CourseRelation.objects.create(course=course, current_lesson=1, creator=self.user)
        rating = RatingFactory(course=course, creator=other_user)
        ActionFactory(content_object=rating, course=course, creator=other_user)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
