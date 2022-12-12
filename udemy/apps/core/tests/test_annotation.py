from django.db.models import Count, Q
from django.test import TestCase, RequestFactory

from udemy.apps.core.annotations import AnnotationBase
from udemy.apps.core.models import ModelTest


class TestAnnotations(AnnotationBase):
    annotation_fields = ('annotation_one', 'annotation_two', 'annotation_list')

    def annotation_one(self):
        return {
            'expression': Count,
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

        generated_dict = self.annotation_class.generate_annotation_dict(annotation_name, self.simple_annotation)
        expected_dict = {'annotation_test': Count('test_expression')}
        assert generated_dict == expected_dict

    def test_generate_complex_annotation_dict(self):
        annotation_name = 'annotation_test'

        generated_dict = self.annotation_class.generate_annotation_dict(annotation_name, self.complex_annotation)
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

        generated_dict = self.annotation_class.generate_annotation_dict(annotation_name, self.simple_annotation,
                                                                        additional_path)
        expected_dict = {
            'test__model__annotation_test': Count('test__model__test_expression')
        }

        assert generated_dict == expected_dict

    def test_generate_complex_annotation_dict_with_additional_path(self):
        annotation_name = 'annotation_test'
        additional_path = 'test__model'

        generated_dict = self.annotation_class.generate_annotation_dict(annotation_name, self.complex_annotation,
                                                                        additional_path)
        expected_dict = {
            'test__model__annotation_test': Count('test__model__test_expression', distinct=True, filter=Q(
                test__model__filter_expression='test',
                test__model__other_expression='other'))
        }

        assert generated_dict == expected_dict

    def test_assemble_annotation(self):
        annotation = self.annotation_class.assemble_annotation('annotation_one')
        expected_annotation = {
            'annotation_one': Count('test_expression')
        }

        assert annotation == expected_annotation

    def test_assemble_annotation_with_additional_path(self):
        annotation = self.annotation_class.assemble_annotation('annotation_one', additional_path='test__model')
        expected_annotation = {
            'test__model__annotation_one': Count('test__model__test_expression')
        }

        assert annotation == expected_annotation

    def test_assemble_annotation_list(self):
        annotation = self.annotation_class.assemble_annotation('annotation_list')
        expected_annotation = {
            'test_3': Count('test_expression_3'),
            'test_2': Count('test_expression_2'),
            'test_1': Count('test_expression_1'),
        }
        assert annotation == expected_annotation

    def test_assemble_annotation_list_with_additional_path(self):
        annotation = self.annotation_class.assemble_annotation('annotation_list', additional_path='test__model')
        expected_annotation = {
            'test__model__test_3': Count('test__model__test_expression_3'),
            'test__model__test_2': Count('test__model__test_expression_2'),
            'test__model__test_1': Count('test__model__test_expression_1'),
        }
        assert annotation == expected_annotation

    def test_get_annotations(self):
        annotations = self.annotation_class.get_annotations('annotation_one', 'annotation_two')
        expected_annotations = {
            'annotation_two': Count('test_expression', distinct=True, filter=Q(
                filter_expression='test',
                other_expression='other'
            )),
            'annotation_one': Count('test_expression'),
        }
        assert annotations == expected_annotations

    def test_get_annotations_with_additional_path(self):
        annotations = self.annotation_class.get_annotations('annotation_one', 'annotation_two', additional_path='test')
        expected_annotations = {
            'test__annotation_two': Count('test__test_expression', distinct=True, filter=Q(
                test__filter_expression='test',
                test__other_expression='other'
            )),
            'test__annotation_one': Count('test__test_expression'),
        }
        assert annotations == expected_annotations

    def test_get_annotations_with_start(self):
        annotations = self.annotation_class.get_annotations('*')
        expected_annotations = {
            'annotation_two': Count('test_expression', distinct=True, filter=Q(
                filter_expression='test',
                other_expression='other'
            )),
            'annotation_one': Count('test_expression'),
            'test_3': Count('test_expression_3'),
            'test_2': Count('test_expression_2'),
            'test_1': Count('test_expression_1'),
        }
        assert annotations == expected_annotations


factory = RequestFactory()
request = factory.get('/')


class TestAnnotationManager(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')

    def test_if_model_annotations_are_being_annotated(self):
        with self.assertNumQueries(1):
            model_test = ModelTest.objects.get(id=self.model_test.id)

            annotation_fields = ('test_field', 'test_1', 'test_2', 'test_3')

            assert all([hasattr(model_test, field) for field in annotation_fields])
