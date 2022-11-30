import re

from django.core.exceptions import FieldDoesNotExist
from django.db.models import ManyToManyField, ForeignKey, ManyToOneRel, Exists, OuterRef
from django.utils.functional import cached_property

from rest_framework.permissions import AllowAny

from udemy.apps.course.models import Course


class RetrieveRelatedObjectMixin:

    @cached_property
    def related_fields(self):
        nested_fields = dict()
        for field_name, fields in self.request.query_params.items():
            match = re.search(r'fields\[([A-Za-z0-9_]+)]', field_name)
            if match:
                nested_fields[match.group(1)] = fields.split(',')
        return nested_fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['fields'] = self.related_fields
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        for field_name in self.related_fields.keys():
            try:
                field = self.Meta.model._meta.get_field(field_name)
                if isinstance(field, ManyToManyField) or isinstance(field, ManyToOneRel):
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


class ActionPermissionMixin:
    permission_classes_by_action = {
        ('default',): [AllowAny],
    }

    def get_permissions_by_action(self, action):
        for actions, permissions in self.permission_classes_by_action.items():
            if action in actions:
                return [permission() for permission in permissions]

    def get_permissions(self):
        permissions = self.get_permissions_by_action(self.action)
        if permissions:
            return permissions
        return self.get_permissions_by_action('default')


class AnnotatePermissionMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            ref_name = 'id' if self.Meta.model == Course else 'course__id'

            queryset = queryset.annotate(is_enrolled=Exists(
                self.request.user.enrolled_courses.filter(id=OuterRef(ref_name))
            )).annotate(is_instructor=Exists(
                self.request.user.instructors_courses.filter(id=OuterRef(ref_name))
            ))

        return queryset
