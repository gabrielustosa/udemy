import re

from rest_framework import status
from rest_framework.response import Response


class ValidateOrderMixin:
    def create(self, request, *args, **kwargs):
        if 'order' in request.data:
            return Response({'order': 'Order is automatically generated.'}, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if 'order' in request.data:
            last_order = self.get_object().get_last_order()
            new_order = int(request.data['order'])
            if new_order > last_order:
                return Response({'order': 'The order can not be greater than last order of the module.'},
                                status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


class RetrieveNestedObjectMixin:

    def get_nested_fields(self):
        nested_fields = dict()
        for field_name, fields in self.request.query_params.items():
            match = re.search(r'fields\[([A-Za-z0-9_]+)]', field_name)
            if match:
                nested_fields[match.group(1)] = fields.split(',')
        return nested_fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['fields'] = self.get_nested_fields()
        return context
