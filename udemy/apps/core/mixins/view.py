import re

from django.core.exceptions import FieldDoesNotExist
from django.db.models import ManyToManyField, ForeignKey, ManyToOneRel, Exists, OuterRef
from django.utils.functional import cached_property

from rest_framework.permissions import AllowAny

from udemy.apps.course.models import Course


class DynamicFieldViewMixin:
    """
    Mixin that takes additional fields in query_params that controls which fields should be displayed

    Example:
        https://example.com/resource/?fields=name,@default
    """

    def get_serializer(self, *args, **kwargs):
        fields = self.request.query_params.get('fields')
        if fields is not None:
            kwargs['fields'] = fields.split(',')
        return super().get_serializer(*args, **kwargs)


class RetrieveRelatedObjectMixin:
    """
    Mixin for API View that optimize queryset with related objects and update the serializer context with related
    objects fields get by query_params.

    Example:
          https://example.com/resource/?fields[related_object_name]=@min,image
    """

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

    def optimize_foreign_field(self, queryset, field):
        queryset = self._optimize_foreign_annotations(queryset, field)
        queryset = self._optimize_foreign_prefetch_related(queryset, field)
        return queryset

    def _optimize_foreign_annotations(self, queryset, field):
        if hasattr(field.related_model, 'annotation_class'):
            annotations = field.related_model.get_annotations('*', related_field=f'{field.name}__')
            queryset = queryset.annotate(**annotations)
        return queryset

    def _optimize_foreign_prefetch_related(self, queryset, field):
        for field_type in field.related_model._meta.get_fields():
            if isinstance(field_type, ManyToManyField):
                queryset = queryset.prefetch_related(f'{field.name}__{field_type.name}')
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        for field_name in self.related_fields.keys():
            try:
                field = self.Meta.model._meta.get_field(field_name)
                if isinstance(field, ManyToManyField) or isinstance(field, ManyToOneRel):
                    queryset = queryset.prefetch_related(field_name)
                if isinstance(field, ForeignKey):
                    queryset = queryset.select_related(field_name)
                    queryset = self.optimize_foreign_field(queryset, field)
            except FieldDoesNotExist:
                pass

        return queryset


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
        return permissions if permissions else self.get_permissions_by_action('default')


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

