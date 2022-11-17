import re

from django.core.exceptions import FieldDoesNotExist
from django.db.models import ManyToManyField, ForeignKey
from django.utils.functional import cached_property


class RetrieveNestedObjectMixin:

    @cached_property
    def get_related_fields(self):
        nested_fields = dict()
        for field_name, fields in self.request.query_params.items():
            match = re.search(r'fields\[([A-Za-z0-9_]+)]', field_name)
            if match:
                nested_fields[match.group(1)] = fields.split(',')
        return nested_fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['fields'] = self.get_related_fields
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        for field_name in self.get_related_fields.keys():
            try:
                field = self.Meta.model._meta.get_field(field_name)
                if isinstance(field, ManyToManyField):
                    queryset = queryset.prefetch_related(field_name)
                if isinstance(field, ForeignKey):
                    queryset = queryset.select_related(field_name)
            except FieldDoesNotExist:
                pass

        return queryset

    def get_serializer(self, *args, **kwargs):
        fields = self.request.query_params.get('fields')
        if fields is not None:
            kwargs['fields'] = fields.split(',')
        return super().get_serializer(*args, **kwargs)
