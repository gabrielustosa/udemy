from parameterized import parameterized

from django.test import TestCase

from rest_framework.reverse import reverse

from tests.factories.course import CourseFactory

from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.module.models import Module


class SerializerDynamicFieldsTests(TestCase):
    def test_dynamic_fields(self):
        course = CourseFactory()
        url = reverse('course-detail', kwargs={'pk': course.id})

        response = self.client.get(f'{url}?fields=title,slug,headline')

        serializer = CourseSerializer(course, fields=('title', 'slug', 'headline'))

        self.assertEqual(response.data, serializer.data)

    @parameterized.expand([
        ('@min',),
        ('@default',)
    ])
    def test_object_fields_types(self, field_type):
        course = CourseFactory()
        url = reverse('course-detail', kwargs={'pk': course.id})

        response = self.client.get(f'{url}?fields={field_type}')

        serializer = CourseSerializer(course, fields=(field_type,))

        self.assertEqual(response.data, serializer.data)

    def test_create_only_fields(self):
        class CreateOnlySerializer(ModelSerializer):
            class Meta:
                model = Course
                fields = ('title', 'headline')
                create_only_fields = ('headline',)

        data = {'title': 'new title', 'headline': 'new headline'}
        serializer = CreateOnlySerializer(instance=CourseFactory(), data=data)
        serializer.is_valid()
        course = serializer.save()

        self.assertIsNotNone(course)
        self.assertEqual(course.title, data['title'])
        self.assertNotEqual(course.headline, data['headline'])

    def test_update_only_fields(self):
        class UpdateOnlySerializer(ModelSerializer):
            class Meta:
                model = Module
                fields = ('title', 'order', 'course')
                update_only_fields = ('order',)

        course = CourseFactory()
        data = {'title': 'title', 'order': '5', 'course': course.id}
        serializer = UpdateOnlySerializer(data=data)
        serializer.is_valid()
        module = serializer.save()

        self.assertIsNotNone(module)
        self.assertEqual(module.title, data['title'])
        self.assertNotEqual(module.order, data['order'])
