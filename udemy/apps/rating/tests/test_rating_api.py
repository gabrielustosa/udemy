from django.test import TestCase
from django.shortcuts import reverse

from parameterized import parameterized

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.action import ActionFactory
from tests.factories.answer import AnswerFactory
from tests.utils import create_factory_in_batch
from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action
from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.user.serializer import UserSerializer

RATING_LIST_URL = reverse('rating:rating-list')


def rating_detail_url(pk): return reverse('rating:rating-detail', kwargs={'pk': pk})


def rating_action_url(pk): return reverse('rating:action-list', kwargs={'rating_id': pk})


def rating_action_url_detail(pk, action):
    return reverse('rating:action-detail', kwargs={'rating_id': pk, 'action': action})


def rating_answer_url(pk): return reverse('rating:answer-list', kwargs={'rating_id': pk})


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

        response = self.client.get(rating_detail_url(pk=rating.id))

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
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cant_rate_a_course_not_enrolled(self):
        course = CourseFactory()

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        actions = create_factory_in_batch(ActionFactory, 10, content_object=rating)

        response = self.client.get(rating_action_url(rating.id))

        actions = ActionSerializer(actions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, actions.data)
        self.assertEqual(rating.actions.count(), 10)

    def test_rating_action_retrieve(self):
        rating = RatingFactory(creator=self.user)
        action = ActionFactory(creator=self.user, content_object=rating)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        serializer = ActionSerializer(action)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_rating_action_retrieve_only_own_user_action(self):
        rating = RatingFactory()
        ActionFactory(content_object=rating)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rating_action_delete(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)
        ActionFactory(creator=self.user, content_object=rating, course=course)

        response = self.client.delete(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Action.objects.filter(id=1).exists())

    def test_user_cant_delete_action_that_is_not_his(self):
        other_user = UserFactory()
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=other_user)
        ActionFactory(content_object=rating, course=course, creator=other_user)

        response = self.client.get(rating_action_url_detail(rating.id, 1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        rating = RatingFactory(course=course, creator=self.user)

        answers = create_factory_in_batch(AnswerFactory, 10, content_object=rating, course=course)

        response = self.client.get(rating_answer_url(rating.id))

        serializer = AnswerSerializer(answers, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @parameterized.expand([
        ('creator', ('id', 'name'), UserSerializer),
        ('course', ('id', 'title'), CourseSerializer),
    ])
    def test_related_objects(self, field_name, fields, Serializer):
        rating = RatingFactory()

        response = self.client.get(
            f'{rating_detail_url(rating.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        rating_serializer = RatingSerializer(rating, fields=('@min',))
        object_serializer = Serializer(getattr(rating, field_name), fields=fields)

        expected_response = {
            **rating_serializer.data,
            field_name: {
                **object_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)
