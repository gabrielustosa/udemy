from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.content import ContentFactory
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.content.models import Content, Text, Link
from udemy.apps.content.serializer import ContentSerializer

CONTENT_LIST_URL = reverse('content-list')


def content_detail_url(pk): return reverse('content-detail', kwargs={'pk': pk})


class PublicContentAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_content_list(self):
        lessons = create_factory_in_batch(ContentFactory, 5)

        response = self.client.get(CONTENT_LIST_URL)

        serializer = ContentSerializer(lessons, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_content_retrieve(self):
        content = ContentFactory()

        response = self.client.get(content_detail_url(pk=1))

        serializer = ContentSerializer(content)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_content(self):
        response = self.client.post(CONTENT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateContentApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_content(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        LessonFactory(course=course)

        payload = {
            'title': 'teste',
            'lesson': 1,
            'course': 1,
            'item': {
                'content': 'Teste'
            }
        }
        response = self.client.post(CONTENT_LIST_URL, payload, format='json')

        content = Content.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content.title, payload['title'])
        self.assertEqual(content.item.content, payload['item']['content'])

    def test_partial_content_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)
        content = ContentFactory(lesson=lesson, course=course)

        payload = {
            'item': {
                'url': 'https://google.com'
            }
        }
        response = self.client.patch(content_detail_url(pk=content.id), payload, format='json')

        content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.item.url, payload['item']['url'])

    def test_content_full_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)
        content = ContentFactory(lesson=lesson, course=course)

        payload = {
            'title': 'teste',
            'lesson': 1,
            'course': 1,
            'item': {
                'url': 'https://google.com'
            }
        }
        response = self.client.put(content_detail_url(pk=lesson.id), payload, format='json')

        content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.title, payload['title'])
        self.assertEqual(content.item.url, payload['item']['url'])

    def test_delete_content(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)
        content = ContentFactory(lesson=lesson, course=course)

        response = self.client.delete(content_detail_url(pk=content.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Content.objects.filter(id=content.id).exists())

    def test_not_course_instructor_cant_create_a_content(self):
        LessonFactory()

        payload = {
            'title': 'teste',
            'lesson': 1,
            'course': 1,
            'item': {
                'content': 'Teste'
            }
        }
        response = self.client.post(CONTENT_LIST_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_update_content(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)
        content = ContentFactory(lesson=lesson, course=course)

        user = UserFactory()
        self.client.force_authenticate(user)

        response_patch = self.client.patch(content_detail_url(pk=content.id))
        response_put = self.client.put(content_detail_url(pk=content.id))

        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_content(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        content = ContentFactory(lesson=lesson, course=course)

        response = self.client.delete(content_detail_url(pk=content.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_send_a_order_greater_than_max_order_content(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)

        create_factory_in_batch(ContentFactory, 5, course=course, lesson=lesson)

        payload = {
            'order': 6,
        }

        response = self.client.patch(content_detail_url(pk=1), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand([
        (3, 6),
        (8, 2),
        (1, 10),
        (9, 2),
        (10, 2),
        (5, 5),
    ])
    def test_content_reorder_field(self, current_order, new_order):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)

        create_factory_in_batch(ContentFactory, 20, course=course, lesson=lesson)

        content = Content.objects.filter(order=current_order).first()

        payload = {
            'order': new_order
        }

        response = self.client.patch(content_detail_url(pk=current_order), payload)

        content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.order, new_order)

        for index, model in enumerate(Content.objects.all(), start=1):
            self.assertEqual(model.order, index)

    @parameterized.expand([
        (Text, {'content': 'Random content'}),
        (Link, {'url': 'https://google.com'}),
    ])
    def test_create_content_link_and_text(self, model, data):
        course = CourseFactory()
        course.instructors.add(self.user)
        LessonFactory(course=course)

        payload = {
            'title': 'teste',
            'lesson': 1,
            'course': 1,
            'item': {
                **data
            }
        }
        response = self.client.post(CONTENT_LIST_URL, payload, format='json')

        content = Content.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(isinstance(content.item, model))
