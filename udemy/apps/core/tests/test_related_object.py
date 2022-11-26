from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from tests.utils import create_factory_in_batch

from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.module.serializer import ModuleSerializer
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.user.serializer import UserSerializer


class RelatedObjectRetrieveTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_related_object_retrieve(self):
        module = ModuleFactory()
        CourseRelation.objects.create(course=module.course, creator=self.user)
        url = reverse('module-detail', kwargs={'pk': module.id})

        response = self.client.get(f'{url}?fields[course]=title,is_paid,slug')

        module_serializer = ModuleSerializer(module)
        course_serializer = CourseSerializer(module.course, fields=('title', 'is_paid', 'slug'))

        expected_response = {
            **module_serializer.data,
            'course': {
                **course_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_retrieve_many_related_objects(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        question = QuestionFactory(course=course)
        url = reverse('question:question-detail', kwargs={'pk': question.id})

        response = self.client.get(f'{url}?fields[creator]=id,name&fields[lesson]=id,title&fields[course]=id,title')

        question_serializer = QuestionSerializer(question)
        creator_serializer = UserSerializer(question.creator, fields=('id', 'name'))
        lesson_serializer = LessonSerializer(question.lesson, fields=('id', 'title'))
        course_serializer = CourseSerializer(question.course, fields=('id', 'title'))

        expected_response = {
            **question_serializer.data,
            'creator': {
                **creator_serializer.data
            },
            'lesson': {
                **lesson_serializer.data
            },
            'course': {
                **course_serializer.data
            }
        }

        self.assertEqual(response.data, expected_response)

    def test_related_object_retrieve_with_invalid_field(self):
        module = ModuleFactory()
        CourseRelation.objects.create(course=module.course, creator=self.user)
        url = reverse('module-detail', kwargs={'pk': module.id})

        response = self.client.get(f'{url}?fields[teste]=title,is_paid,slug')

        serializer = ModuleSerializer(module)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_related_object_retrieve_m2m(self):
        course = CourseFactory()
        instructors = create_factory_in_batch(UserFactory, 5)
        instructors.insert(0, self.user)
        course.instructors.add(*instructors)
        url = reverse('course-detail', kwargs={'pk': course.id})

        response = self.client.get(f'{url}?fields[instructors]=id,name')

        course_serializer = CourseSerializer(course)
        user_serializer = UserSerializer(instructors, many=True, fields=('id', 'name'))

        expected_response = {
            **course_serializer.data,
            'instructors': user_serializer.data
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_retrieve_many_to_one_object(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user)
        url = reverse('course-detail', kwargs={'pk': course.id})

        lessons = create_factory_in_batch(LessonFactory, 5, course=course, module__course=course)

        response = self.client.get(f'{url}?fields[lessons]=id,title')

        serializer = LessonSerializer(lessons, many=True, fields=('id', 'title'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lessons'], serializer.data)

    def test_related_object_permission(self):
        course = CourseFactory()
        url = reverse('course-detail', kwargs={'pk': course.id})

        response = self.client.get(f'{url}?fields[modules]=id')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
