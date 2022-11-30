from django.test import TestCase
from django.shortcuts import reverse

from parameterized import parameterized

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.action import RatingActionFactory
from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory

from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.course.models import CourseRelation


def rating_action_url(pk): return reverse('rating:action-list', kwargs={'rating_id': pk})


def rating_action_url_detail(pk, action):
    return reverse('rating:action-detail', kwargs={'rating_id': pk, 'action': action})


class TestRatingAction(TestCase):
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
        rating = RatingFactory(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'action': action,
        }

        response = self.client.post(rating_action_url(rating.id), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rating.actions.filter(action=action).count(), 1)

    def test_action_rating_list(self):
        rating = RatingFactory()
        actions = RatingActionFactory.create_batch(10, content_object=rating)

        response = self.client.get(rating_action_url(rating.id))

        actions = ActionSerializer(actions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, actions.data)
        self.assertEqual(rating.actions.count(), 10)

    def test_rating_action_retrieve(self):
        rating = RatingFactory(creator=self.user)
        action = RatingActionFactory(content_object=rating, action=1)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        serializer = ActionSerializer(action)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_rating_action_delete(self):
        rating = RatingFactory(creator=self.user)
        CourseRelation.objects.create(course=rating.course, creator=self.user)
        action = RatingActionFactory(content_object=rating, action=1)

        response = self.client.delete(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.objects.filter(id=action.id).exists())

    def test_rating_action_retrieve_only_own_user_action(self):
        rating = RatingFactory()
        RatingActionFactory(content_object=rating, action=1)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cant_delete_rating_action_that_is_not_his(self):
        other_user = UserFactory()
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=other_user)
        RatingActionFactory(content_object=rating)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
