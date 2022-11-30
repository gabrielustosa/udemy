from random import randint

from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer

LESSON_LIST_URL = reverse('lesson-list')


def lesson_detail_url(pk): return reverse('lesson-detail', kwargs={'pk': pk})


class TestAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_lesson(self):
        module = ModuleFactory()
        module.course.instructors.add(self.user)

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'module': module.id,
            'course': module.course.id
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        lesson = Lesson.objects.get(id=response.data['id'])

        serializer = LessonSerializer(lesson)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_lesson_retrieve(self):
        lesson = LessonFactory()
        CourseRelation.objects.create(course=lesson.course, creator=self.user)

        response = self.client.get(lesson_detail_url(pk=lesson.id))

        serializer = LessonSerializer(lesson)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_partial_lesson_update(self):
        lesson = LessonFactory()

        lesson.course.instructors.add(self.user)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_lesson_full_update(self):
        lesson = LessonFactory()

        lesson.course.instructors.add(self.user)

        payload = {
            'title': 'new title',
            'video': 'https://www.youtube.com/watch?v=dawjkb_dwadaws',
        }
        response = self.client.put(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_delete_lesson(self):
        lesson = LessonFactory()

        lesson.course.instructors.add(self.user)

        response = self.client.delete(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())


class TestLessonOrder(TestCase):
    """
    Test content model order.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    @parameterized.expand([
        (3, 6),
        (8, 2),
        (1, 10),
        (9, 2),
        (10, 2),
        (5, 5),
    ])
    def test_lesson_reorder_field(self, current_order, new_order):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        course.instructors.add(self.user)

        LessonFactory.create_batch(10, course=course, module=module)

        lesson = Lesson.objects.filter(order=current_order).first()

        payload = {
            'order': new_order
        }

        response = self.client.patch(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.order, new_order)

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)

    def test_order_lesson_is_generated_correctly(self):
        course = CourseFactory()
        modules = ModuleFactory.create_batch(5, course=course)
        course.instructors.add(self.user)

        LessonFactory.create_batch(25, course=course, module=modules[randint(0, 4)])

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)

