import re

from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db.models import ManyToManyField, ForeignKey, ManyToOneRel, Exists, OuterRef, F
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
    expanded_foreign_fields = dict()
    expanded_m2m_fields = dict()

    @cached_property
    def related_fields(self):
        nested_fields = dict()
        for field_name, fields in self.request.query_params.items():
            match = re.search(r'fields\[([A-Za-z0-9_]+)]', field_name)
            if match:
                nested_fields[match.group(1)] = fields.split(',')
        return nested_fields

    @cached_property
    def expanded_fields(self):
        expanded_fields = dict()
        for related_object, fields in self.related_fields.items():
            for field in fields:
                if '__' in field:
                    expanded_fields.setdefault(related_object, []).append(field)
        return expanded_fields

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['fields'] = self.related_fields
        context['expanded_foreign_fields'] = self.expanded_foreign_fields
        context['expanded_m2m_fields'] = self.expanded_m2m_fields
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        for field_name in self.related_fields.keys():
            try:
                field = self.Meta.model._meta.get_field(field_name)
                if isinstance(field, ManyToManyField) or isinstance(field, ManyToOneRel):
                    queryset = queryset.prefetch_related(field_name)

                    expanded_fields = self.expanded_fields.get(field_name)
                    if expanded_fields:
                        self.expanded_m2m_fields[field_name] = expanded_fields

                if isinstance(field, ForeignKey):
                    queryset = queryset.select_related(field_name)

                    expanded_fields = self.expanded_fields.get(field_name, [])
                    for expanded_field in expanded_fields:
                        try:
                            kwargs = {f'{field_name}_{expanded_field}': F(f'{field_name}__{expanded_field}')}
                            queryset = queryset.annotate(**kwargs)

                            fields = self.expanded_foreign_fields.setdefault(field_name, [])
                            if expanded_field not in fields:
                                fields.append(expanded_field)
                        except FieldError:
                            pass

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


class AnnotateModelMixin:
    def get_annotation_fields(self):
        method_fields = set(self.Meta.model.annotations_fields)
        serializer_fields = self.request.query_params.get('fields')

        if serializer_fields is None:
            return method_fields

        serializer_fields = set(serializer_fields.split(','))

        return method_fields.intersection(serializer_fields)

    def get_queryset(self):
        queryset = super().get_queryset()

        annotation_fields = self.get_annotation_fields()
        annotations = self.Meta.model.get_annotations(*annotation_fields)
        queryset = queryset.annotate(**annotations)

        return queryset
