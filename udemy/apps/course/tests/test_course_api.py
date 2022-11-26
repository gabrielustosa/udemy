from decimal import Decimal

from django.test import TestCase
from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.utils import create_factory_in_batch
from tests.factories.category import CategoryFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.content.serializer import ContentSerializer

from udemy.apps.course.models import Course, CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.message.serializer import MessageSerializer
from udemy.apps.module.serializer import ModuleSerializer
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.quiz.serializer import QuizSerializer
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.user.serializer import UserSerializer

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


class PrivateCourseApiTests(TestCase):
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

        course = Course.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(self.user, course.instructors.all())

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(course.instructors.first(), self.user)

    def test_delete_course(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        response = self.client.delete(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_user_not_instructor_cant_patch_course(self):
        course = CourseFactory()

        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.patch(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_put_course(self):
        course = CourseFactory()

        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.put(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_course(self):
        course = CourseFactory()

        response = self.client.delete(course_detail_url(pk=course.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        ('instructors', ('id', 'name'), UserSerializer),
        ('categories', ('id', 'title'), CategorySerializer),
        ('quizzes', ('id', 'title'), QuizSerializer),
        ('lessons', ('id', 'title'), LessonSerializer),
        ('modules', ('id', 'title'), ModuleSerializer),
        ('contents', ('id', 'title'), ContentSerializer),
        ('ratings', ('id', 'comment'), RatingSerializer),
        ('warning_messages', ('id', 'title'), MessageSerializer),
        ('questions', ('id', 'title'), QuestionSerializer),
    ])
    def test_related_objects_m2m(self, field_name, fields, Serializer):
        course = CourseFactory()
        CourseRelation.objects.create(creator=self.user, course=course)

        response = self.client.get(
            f'{course_detail_url(course.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        course_serializer = CourseSerializer(course, fields=('@min',))
        object_serializer = Serializer(getattr(course, field_name).all(), fields=fields, many=True)

        expected_response = {
            **course_serializer.data,
            field_name: object_serializer.data
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)
