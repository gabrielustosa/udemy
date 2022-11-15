from random import randint

from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer

LESSON_LIST_URL = reverse('lesson-list')


def lesson_detail_url(pk): return reverse('lesson-detail', kwargs={'pk': pk})


class PublicLessonAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_lesson_list(self):
        lessons = create_factory_in_batch(LessonFactory, 5)

        response = self.client.get(LESSON_LIST_URL)

        serializer = LessonSerializer(lessons, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_lesson_retrieve(self):
        lesson = LessonFactory()

        response = self.client.get(lesson_detail_url(pk=1))

        serializer = LessonSerializer(lesson)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_lesson(self):
        response = self.client.post(LESSON_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLessonApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_lesson(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        ModuleFactory(course=course)

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'video_id': 'E6CdIawPTh0',
            'video_duration': 1,
            'module': 1,
            'course': 1
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        lesson = Lesson.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(lesson.title, payload['title'])
        self.assertEqual(lesson.video, payload['video'])

    def test_partial_lesson_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)
        lesson = LessonFactory(module=module, course=course)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_lesson_full_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)
        lesson = LessonFactory(module=module, course=course)

        payload = {
            'title': 'new title',
            'video': 'https://www.youtube.com/watch?v=dawjkb_dwadaws',
            'video_id': 'E6CzwPTh0',
            'video_duration': 10,
            'module': 1,
            'course': 1
        }
        response = self.client.put(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_delete_lesson(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)
        lesson = LessonFactory(course=course, module=module)

        response = self.client.delete(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())

    def test_not_course_instructor_cant_create_a_lesson(self):
        course = CourseFactory()
        ModuleFactory(course=course)

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'video_id': 'E6CdIawPTh0',
            'video_duration': 1,
            'module': 1,
            'course': 1
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_update_lesson(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        lesson = LessonFactory(course=course, module=module)

        user = UserFactory()
        self.client.force_authenticate(user)

        response_patch = self.client.patch(lesson_detail_url(pk=lesson.id))
        response_put = self.client.put(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_lesson(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        lesson = LessonFactory(course=course, module=module)

        response = self.client.delete(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_send_a_order_greater_than_max_order_lesson(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        course.instructors.add(self.user)

        create_factory_in_batch(LessonFactory, 5, course=course, module=module)

        payload = {
            'order': 6,
        }

        response = self.client.patch(lesson_detail_url(pk=1), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        create_factory_in_batch(LessonFactory, 10, course=course, module=module)

        lesson = Lesson.objects.filter(order=current_order).first()

        payload = {
            'order': new_order
        }

        response = self.client.patch(lesson_detail_url(pk=current_order), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.order, new_order)

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)

    def test_order_lesson_is_generated_correctly(self):
        course = CourseFactory()
        modules = create_factory_in_batch(ModuleFactory, 5, course=course)
        course.instructors.add(self.user)

        create_factory_in_batch(LessonFactory, 25, module=modules[0])

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)
