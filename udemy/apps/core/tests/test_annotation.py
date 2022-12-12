from django.db.models import Count, Q, Sum
from django.test import TestCase
from rest_framework.fields import IntegerField

from udemy.apps.core.annotations import AnnotationBase
from udemy.apps.core.fields import AnnotationDictField
from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class TestAnnotations(AnnotationBase):

    def annotation_one(self):
        return {
            'expression': Sum,
            'query_expression': 'test_expression'
        }

    def annotation_two(self):
        return {
            'expression': Count,
            'query_expression': 'test_expression',
            'filter_expressions': {'filter_expression': 'test', 'other_expression': 'other'},
            'extra_kwargs': {'distinct': True}
        }

    def annotation_list(self):
        return [{
            'annotation_name': f'test_{option}',
            'expression': Count,
            'query_expression': f'test_expression_{option}'
        } for option in ['1', '2', '3']]


class TestAnnotation(TestCase):
    def setUp(self):
        self.annotation_class = TestAnnotations()
        self.simple_annotation = {
            'expression': Count,
            'query_expression': 'test_expression'
        }
        self.complex_annotation = {
            'expression': Count,
            'query_expression': 'test_expression',
            'filter_expressions': {'filter_expression': 'test', 'other_expression': 'other'},
            'extra_kwargs': {'distinct': True}
        }

    def test_generate_annotation_dict(self):
        annotation_name = 'annotation_test'

        generated_dict = self.annotation_class._generate_annotation_dict(annotation_name, self.simple_annotation)
        expected_dict = {'annotation_test': Count('test_expression')}
        assert generated_dict == expected_dict

    def test_generate_complex_annotation_dict(self):
        annotation_name = 'annotation_test'

        generated_dict = self.annotation_class._generate_annotation_dict(annotation_name, self.complex_annotation)
        expected_dict = {
            'annotation_test': Count('test_expression', distinct=True, filter=Q(
                filter_expression='test',
                other_expression='other'
            ))
        }

        assert generated_dict == expected_dict

    def test_generate_annotation_dict_with_additional_path(self):
        annotation_name = 'annotation_test'
        additional_path = 'test__model'

        generated_dict = self.annotation_class._generate_annotation_dict(annotation_name, self.simple_annotation,
                                                                         additional_path)
        expected_dict = {
            'test__model__annotation_test': Count('test__model__test_expression')
        }

        assert generated_dict == expected_dict

    def test_generate_complex_annotation_dict_with_additional_path(self):
        annotation_name = 'annotation_test'
        additional_path = 'test__model'

        generated_dict = self.annotation_class._generate_annotation_dict(annotation_name, self.complex_annotation,
                                                                         additional_path)
        expected_dict = {
            'test__model__annotation_test': Count('test__model__test_expression', distinct=True, filter=Q(
                test__model__filter_expression='test',
                test__model__other_expression='other'))
        }

        assert generated_dict == expected_dict

    def test_assemble_annotation(self):
        annotation = self.annotation_class._assemble_annotation('annotation_one')
        expected_annotation = {
            'annotation_one': Sum('test_expression')
        }

        assert annotation == expected_annotation

    def test_assemble_annotation_with_additional_path(self):
        annotation = self.annotation_class._assemble_annotation('annotation_one', additional_path='test__model')
        expected_annotation = {
            'test__model__annotation_one': Sum('test__model__test_expression')
        }

        assert annotation == expected_annotation

    def test_assemble_annotation_list(self):
        annotation = self.annotation_class._assemble_annotation('annotation_list')
        expected_annotation = {
            'test_3': Count('test_expression_3'),
            'test_2': Count('test_expression_2'),
            'test_1': Count('test_expression_1'),
        }
        assert annotation == expected_annotation

    def test_assemble_annotation_list_with_additional_path(self):
        annotation = self.annotation_class._assemble_annotation('annotation_list', additional_path='test__model')
        expected_annotation = {
            'test__model__test_3': Count('test__model__test_expression_3'),
            'test__model__test_2': Count('test__model__test_expression_2'),
            'test__model__test_1': Count('test__model__test_expression_1'),
        }
        assert annotation == expected_annotation

    def test_get_annotations(self):
        annotations = self.annotation_class._get_annotations('annotation_one', 'annotation_two')
        expected_annotations = {
            'annotation_two': Count('test_expression', distinct=True, filter=Q(
                filter_expression='test',
                other_expression='other'
            )),
            'annotation_one': Sum('test_expression'),
        }
        assert annotations == expected_annotations

    def test_get_annotations_with_additional_path(self):
        annotations = self.annotation_class._get_annotations('annotation_one', 'annotation_two', additional_path='test')
        expected_annotations = {
            'test__annotation_two': Count('test__test_expression', distinct=True, filter=Q(
                test__filter_expression='test',
                test__other_expression='other'
            )),
            'test__annotation_one': Sum('test__test_expression'),
        }
        assert annotations == expected_annotations

    def test_get_annotations_with_start(self):
        annotations = self.annotation_class._get_annotations('*')
        expected_annotations = {
            'annotation_two': Count('test_expression', distinct=True, filter=Q(
                filter_expression='test',
                other_expression='other'
            )),
            'annotation_one': Sum('test_expression'),
            'test_3': Count('test_expression_3'),
            'test_2': Count('test_expression_2'),
            'test_1': Count('test_expression_1'),
        }
        assert annotations == expected_annotations

    def test_annotations_field_property(self):
        assert self.annotation_class._annotation_fields == ['annotation_list', 'annotation_one', 'annotation_two']


class TestAnnotationManager(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')

    def test_if_model_annotations_are_being_annotated(self):
        with self.assertNumQueries(1):
            model_test = ModelTest.objects.get(id=self.model_test.id)

            annotation_fields = ('test_field', 'test_1', 'test_2', 'test_3')

            assert all([hasattr(model_test, field) for field in annotation_fields])


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')


class TestAnnotationSerializer(TestCase):
    def setUp(self):
        self.annotation_class = TestAnnotations()

    def test_annotation_rest_serializer_field(self):
        annotation_info = self.annotation_class._get_annotation_info('annotation_two')
        rest_serializer_field = self.annotation_class._get_rest_serializer_field(annotation_info, 'annotation_two')

        assert rest_serializer_field == IntegerField

    def test_annotation_rest_serializer_field_assert_error(self):
        annotation_info = self.annotation_class._get_annotation_info('annotation_one')
        with self.assertRaises(AssertionError):
            self.annotation_class._get_rest_serializer_field(annotation_info, 'annotation_one')

    def test_annotation_serializer_field(self):
        serializer_field = self.annotation_class._get_annotation_serializer_field('annotation_two')

        assert isinstance(serializer_field, IntegerField)

    def test_annotation_serializer_field_list(self):
        serializer_field = self.annotation_class._get_annotation_serializer_field('annotation_list')

        assert isinstance(serializer_field, AnnotationDictField)

    def test_annotation_fields_in_serializer_fields(self):
        serializer = ModelTestSerializer()

        fields = serializer.get_fields()

        assert 'custom_field' in fields
        assert 'test_field' in fields


class TestAnnotationDictField(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='a')

    def test_dict_annotation_value(self):
        model_test = ModelTest.objects.get(id=self.model_test.id)

        dict_field = model_test.annotation_class._get_annotation_serializer_field('custom_field')

        attribute = dict_field.get_attribute(model_test)
        expected_attribute = {
            'test_1': 0,
            'test_2': 0,
            'test_3': 0
        }

        assert attribute == expected_attribute
