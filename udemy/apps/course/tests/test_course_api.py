from decimal import Decimal

from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.utils import create_factory_in_batch
from tests.factories.category import CategoryFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer

COURSE_LIST_URL = reverse('course-list')


def course_detail_url(pk): return reverse('course-detail', kwargs={'pk': pk})


class PublicCourseAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_course_list(self):
        courses = create_factory_in_batch(CourseFactory, 5)

        response = self.client.get(COURSE_LIST_URL)

        serializer = CourseSerializer(courses, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], list(reversed(serializer.data)))

    def test_course_retrieve(self):
        course = CourseFactory()

        response = self.client.get(course_detail_url(pk=1))

        serializer = CourseSerializer(course)
        data = {
            'details': serializer.data
        }

        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_course(self):
        response = self.client.post(COURSE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCourseApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_course(self):
        CategoryFactory()
        payload = {
            'title': 'string',
            'slug': 'slug',
            'headline': 'headline',
            'is_paid': True,
            'price': Decimal(1),
            'language': 'english',
            'categories': [1],
            'instructors': [1]
        }
        response = self.client.post(COURSE_LIST_URL, payload)

        course = Course.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(course.instructors.first(), self.user)

    def test_partial_course_update(self):
        original_slug = 'original_slug'
        course = CourseFactory(slug=original_slug)
        course.instructors.add(self.user)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(course_detail_url(pk=course.id), payload)

        course.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(course.title, payload['title'])
        self.assertEqual(course.slug, original_slug)
        self.assertEqual(course.instructors.first(), self.user)

    def test_course_full_update(self):
        CategoryFactory()
        course = CourseFactory()
        course.instructors.add(self.user)

        payload = {
            'title': 'string',
            'slug': 'slug',
            'headline': 'headline',
            'is_paid': True,
            'price': Decimal(1),
            'language': 'english',
            'categories': [1],
            'instructors': [1]
        }
        response = self.client.put(course_detail_url(pk=course.id), payload)

        course.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(course.instructors.first(), self.user)

    def test_delete_course(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        response = self.client.delete(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_user_not_instructor_cant_update_course(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        user = UserFactory()
        self.client.force_authenticate(user)

        response_patch = self.client.patch(course_detail_url(pk=course.id))
        response_put = self.client.put(course_detail_url(pk=course.id))

        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_course(self):
        course = CourseFactory()

        response = self.client.delete(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
