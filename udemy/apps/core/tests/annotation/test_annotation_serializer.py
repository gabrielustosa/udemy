from django.test import TestCase
from rest_framework.fields import IntegerField

from udemy.apps.core.fields import AnnotationDictField, AnnotationField
from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.tests.annotation.test_annotation_base import TestAnnotations


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')


class TestAnnotationSerializer(TestCase):
    def setUp(self):
        self.annotation_class = TestAnnotations()
        self.model_test = ModelTest.objects.create(title='a')

    def test_annotation_rest_serializer_field(self):
        annotation_info = self.annotation_class.get_annotation('annotation_two')
        rest_serializer_field = self.annotation_class.get_rest_serializer_field(annotation_info, 'annotation_two')

        assert isinstance(rest_serializer_field, IntegerField)

    def test_annotation_rest_serializer_field_assert_error(self):
        annotation_info = self.annotation_class.get_annotation('annotation_one')
        with self.assertRaises(AssertionError):
            self.annotation_class.get_rest_serializer_field(annotation_info, 'annotation_one')

    def test_annotation_serializer_field(self):
        serializer_field = self.annotation_class.get_annotation_serializer_field('annotation_two')

        assert isinstance(serializer_field, AnnotationField)

    def test_annotation_serializer_field_list(self):
        serializer_field = self.annotation_class.get_annotation_serializer_field('annotation_list')

        assert isinstance(serializer_field, AnnotationDictField)

    def test_annotation_fields_in_serializer_fields(self):
        serializer = ModelTestSerializer()

        fields = serializer.get_fields()

        assert 'custom_field' in fields
        assert 'test_field' in fields

    def test_annotation_in_serializer_data(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)

        expected_data = {
            'id': model_test.id,
            'title': model_test.title,
            'test_field': 'test field',
            'custom_field': {
                'test_1': 0,
                'test_2': 0,
                'test_3': 0,
            }
        }

        assert serializer.data == expected_data
