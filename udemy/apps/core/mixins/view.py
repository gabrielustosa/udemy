import re

from django.db.models import Exists, OuterRef
from django.utils.functional import cached_property

from rest_framework.permissions import AllowAny

from udemy.apps.course.models import Course


class AnnotationViewMixin:
    """
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        model = self.get_serializer_class().Meta.model

        annotation_class = getattr(model, 'annotation_class', None)
        if annotation_class:
            annotations = None

            fields = self.request.query_params.get('fields')
            if fields:
                annotations = annotation_class.get_annotations(fields)

            if annotations is None:
                annotations = annotation_class.get_annotations('*')

            queryset = queryset.annotate(**annotations)

        return queryset


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


class RelatedObjectViewMixin:
    """
    Mixin for API View that optimize queryset with related objects and update the serializer context with related
    objects fields get by query_params.

    Example:
          https://example.com/resource/?fields[related_object_name]=@min,image
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self.get_auto_optimized_queryset(queryset)

        return queryset

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
        context['related_fields'] = self.related_fields
        return context

    def get_auto_optimized_queryset(self, queryset):
        serializer = self.get_serializer_class()(context={'related_fields': self.related_fields})
        queryset = serializer.auto_optimize_related_object(queryset)
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
            ref_name = 'id' if self.get_serializer_class().Meta.model == Course else 'course__id'

            queryset = queryset.annotate(is_enrolled=Exists(
                self.request.user.enrolled_courses.filter(id=OuterRef(ref_name))
            )).annotate(is_instructor=Exists(
                self.request.user.instructors_courses.filter(id=OuterRef(ref_name))
            ))

        return queryset

