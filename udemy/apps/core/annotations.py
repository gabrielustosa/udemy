from collections import ChainMap, OrderedDict

from django.db import models

from rest_framework import fields as rest_fields

from udemy.apps.core.fields import AnnotationDictField
from udemy.apps.core.middleware import get_current_request


class AnnotationBase:
    def _get_annotation_serializer_fields(self):
        annotation_fields = OrderedDict()

        for annotation_name in self.annotation_fields:
            serializer_field = self._get_annotation_serializer_field(annotation_name)
            annotation_fields[annotation_name] = serializer_field

        return annotation_fields

    def _get_annotation_serializer_field(self, annotation_name):
        annotation_info = self.get_annotation_info(annotation_name)

        if isinstance(annotation_info, list):
            annotation_fields = [annotation['annotation_name'] for annotation in annotation_info]
            return AnnotationDictField(annotation_fields=annotation_fields, read_only=True)

        extra_kwargs = annotation_info.pop('extra_kwargs', {})
        output_field = extra_kwargs.pop('output_field', None)

        if output_field is None:
            expression = annotation_info.pop('expression')

            assert isinstance(
                expression.output_field, models.Field
            ), f'You must declare the output_field of the annotation `{annotation_name}`'

            output_field = expression.output_field

        output_name = output_field.__class__.__name__
        return vars(rest_fields)[output_name](read_only=True)

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
            annotation_name = f'{additional_path}__{annotation_name}'
            query_expression = f'{additional_path}__{query_expression}'

            if filter_expressions:
                filter_expressions = {f'{additional_path}__{key}': value for key, value in filter_expressions.items()}

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
        if '*' in fields:
            fields = self.annotation_fields

        annotations_list = [
            self.assemble_annotation(field, additional_path)
            for field in fields if field in self.annotation_fields
        ]
        return dict(ChainMap(*annotations_list))


class AnnotationManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset()
        annotation_fields = ('*',)

        current_request = get_current_request()
        print(current_request)
        if current_request:
            fields = current_request.GET.get('fields')
            if fields:
                fields = set(fields.split(','))
                avaliable_fields = set(self.model.annotation_class.annotation_fields)
                annotation_fields = avaliable_fields.intersection(fields)

        annotations = self.model.annotation_class.get_annotations(*annotation_fields)

        return queryset.annotate(**annotations)
