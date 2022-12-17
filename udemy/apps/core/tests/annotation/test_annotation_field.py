from django.test import TestCase
from rest_framework.fields import CharField, IntegerField

from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')


class TestAnnotationField(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='a')

    def test_annotation_field_child(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_field = serializer.get_fields()['test_field']

        assert isinstance(annotation_field.child, CharField)

    def test_annotation_field_get_attribute(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_field = serializer.get_fields()['test_field']
        annotation_field.bind('test_field', serializer)

        assert annotation_field.get_attribute(model_test) == 'test field'

    def test_annotation_field_to_representation(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_field = serializer.get_fields()['test_field']

        assert annotation_field.to_representation(1) == '1'


class TestAnnotationDictField(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='a')

    def test_annotation_dict_children_is_bound(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_dict_field = serializer.get_fields()['custom_field']
        annotation_dict_field.bind('custom_field', serializer)

        child_parents = [child.parent for child in annotation_dict_field.children.values()]
        assert all([parent == serializer for parent in child_parents])

    def test_annotation_dict_field_get_attribute(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_dict_field = serializer.get_fields()['custom_field']
        annotation_dict_field.bind('custom_field', serializer)

        expected_attribute = {
            'test_1': 0,
            'test_2': 0,
            'test_3': 0,
        }

        assert annotation_dict_field.get_attribute(model_test) == expected_attribute

    def test_annotation_dict_field_to_representation(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        serializer = ModelTestSerializer(model_test)
        annotation_dict_field = serializer.get_fields()['custom_field']
        annotation_dict_field.bind('custom_field', serializer)

        representation = annotation_dict_field.to_representation({
            'test_1': '0',
            'test_2': '0',
            'test_3': '0',
        })
        expected_representation = {
            'test_1': 0,
            'test_2': 0,
            'test_3': 0,
        }

        assert representation == expected_representation
