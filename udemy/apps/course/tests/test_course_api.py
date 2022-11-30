from decimal import Decimal

from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.category import CategoryFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer

COURSE_LIST_URL = reverse('course-list')


def course_detail_url(pk): return reverse('course-detail', kwargs={'pk': pk})


class TestCourseUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_course_list(self):
        courses = CourseFactory.create_batch(5)

        response = self.client.get(COURSE_LIST_URL)

        serializer = CourseSerializer(courses, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, list(reversed(serializer.data)))

    def test_course_retrieve(self):
        course = CourseFactory()

        response = self.client.get(course_detail_url(pk=course.id))

        serializer = CourseSerializer(course)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_course(self):
        response = self.client.post(COURSE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_course(self):
        category = CategoryFactory()
        payload = {
            'title': 'string',
            'slug': 'slug',
            'headline': 'headline',
            'is_paid': True,
            'price': Decimal(1),
            'language': 'english',
            'requirements': 'requirements',
            'what_you_will_learn': 'you learn',
            'description': 'description',
            'level': 'beginner',
            'categories': [category.id],
            'instructors': [self.user.id]
        }
        response = self.client.post(COURSE_LIST_URL, payload)

        course = Course.objects.get(id=response.data['id'])

        serializer = CourseSerializer(course)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

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

    def test_full_course_update(self):
        category = CategoryFactory()
        course = CourseFactory()
        course.instructors.add(self.user)

        payload = {
            'title': 'string',
            'slug': 'slug',
            'headline': 'headline',
            'is_paid': True,
            'price': Decimal(1),
            'language': 'english',
            'requirements': 'requirements',
            'what_you_will_learn': 'you learn',
            'description': 'description',
            'level': 'beginner',
            'categories': [category.id],
            'instructors': [self.user.id]
        }
        response = self.client.put(course_detail_url(pk=course.id), payload)

        course.refresh_from_db()

        serializer = CourseSerializer(course)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_course(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        response = self.client.delete(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())
