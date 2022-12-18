import inspect

from collections import ChainMap, OrderedDict

from django.db import models
from django.utils.functional import cached_property

from rest_framework.serializers import ModelSerializer

from udemy.apps.core.fields import AnnotationDictField, AnnotationField
from udemy.apps.core.middleware import get_current_request

QUERYSET_DELIMITER = '__'


class AnnotationBase:
    def get_annotation_serializer_fields(self):
        annotation_fields = OrderedDict()

        for annotation_name in self.annotation_fields:
            annotation_fields[annotation_name] = self.get_annotation_serializer_field(annotation_name)

        return annotation_fields

    def get_rest_serializer_field(self, annotation_info, annotation_name):
        extra_kwargs = annotation_info.pop('extra_kwargs', {})
        output_field = extra_kwargs.pop('output_field', None)

        if output_field is None:
            expression = annotation_info.pop('expression')

            assert isinstance(
                expression.output_field, models.Field
            ), f'You must declare the output_field of the annotation `{annotation_name}`'

            output_field = expression.output_field

        return ModelSerializer.serializer_field_mapping.get(output_field.__class__)()

    def get_annotation_serializer_field(self, annotation_name):
        annotation_info = self.get_annotation_info(annotation_name)

        if isinstance(annotation_info, list):
            children = [
                AnnotationField(
                    annotation_name=annotation['annotation_name'],
                    child=self.get_rest_serializer_field(annotation, annotation['annotation_name'])
                )
                for annotation in annotation_info
            ]
            return AnnotationDictField(children=children)

        serializer_field = self.get_rest_serializer_field(annotation_info, annotation_name)
        return AnnotationField(child=serializer_field)

    def get_annotation_info(self, annotation_name):
        annotation = getattr(self, annotation_name, None)
        if annotation is None:
            return None
        return annotation()

    def generate_annotation_dict(self, annotation_name, annotation_info, additional_path=None):
        expression = annotation_info.pop('expression')
        query_expression = annotation_info.pop('query_expression')
        filter_expressions = annotation_info.pop('filter_expressions', None)
        extra_kwargs = annotation_info.pop('extra_kwargs', {})

        if additional_path is not None:
            annotation_name = f'{additional_path}{QUERYSET_DELIMITER}{annotation_name}'
            query_expression = f'{additional_path}{QUERYSET_DELIMITER}{query_expression}'

            if filter_expressions:
                filter_expressions = {f'{additional_path}{QUERYSET_DELIMITER}{key}': value
                                      for key, value in filter_expressions.items()}

        if filter_expressions:
            extra_kwargs.update({'filter': models.Q(**filter_expressions)})

        return {annotation_name: expression(query_expression, **extra_kwargs)}

    def assemble_annotation(self, annotation_name, additional_path=None):
        annotation_info = self.get_annotation_info(annotation_name)

        if isinstance(annotation_info, list):
            annotations_list = [
                self.generate_annotation_dict(annotation['annotation_name'], annotation, additional_path)
                for annotation in annotation_info
            ]
            return dict(ChainMap(*annotations_list))

        return self.generate_annotation_dict(annotation_name, annotation_info, additional_path)

    def get_annotations(self, *fields, additional_path=None):
        fields = self._intersection_fields(fields)

        if '*' in fields:
            fields = self.annotation_fields

        annotations_list = [
            self.assemble_annotation(field, additional_path)
            for field in fields if field in self.annotation_fields
        ]
        return dict(ChainMap(*annotations_list))

    def _intersection_fields(self, fields):
        if '@all' in fields or '*' in fields:
            return self.annotation_fields

        return set(self.annotation_fields).intersection(fields)

    @cached_property
    def annotation_fields(self):
        annotation_fields = []
        for klass in [klass for klass in self.__class__.mro() if klass.__name__ != 'AnnotationBase']:
            for name, attr in vars(klass).items():
                if inspect.isfunction(attr):
                    assert QUERYSET_DELIMITER not in name, f'Do not use `{QUERYSET_DELIMITER}` in annotations names'
                    annotation_fields.append(name)
        return annotation_fields

class AnnotationManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset()
        annotations = self.model.annotation_class.get_annotations('*')

        current_request = get_current_request()
        if current_request:
            fields = current_request.GET.get('fields')
            if fields:
                annotations = self.model.annotation_class.get_annotations(fields)

        return queryset.annotate(**annotations)
