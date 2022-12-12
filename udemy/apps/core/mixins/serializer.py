from django.db.models import Manager, ManyToManyField
from django.utils.module_loading import import_string

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny

from udemy.apps.core.paginator import PaginatorRelatedObject


class RelatedObjetsOptimizeMixin:
    def optimize_queryset(self, queryset, related_object):
        queryset = self._optimize_queryset_prefetch_related(queryset, related_object)
        queryset = self._optimize_queryset_annotations(queryset, related_object)
        return queryset

    def optimize_related_object(self, instance, related_object):
        related_object = self._optimize_related_object_annotations(instance, related_object)
        return related_object

    def _optimize_related_object_annotations(self, instance, related_object):
        if hasattr(related_object, 'annotation_class'):
            annotations = related_object._get_annotations('*')
            model_name = related_object.__class__.__name__.lower()
            for annotation_name in annotations.keys():
                value = getattr(instance, f'{model_name}__{annotation_name}', None)
                setattr(related_object, annotation_name, value)
        return related_object

    def _optimize_queryset_annotations(self, queryset, related_object):
        if hasattr(related_object.model, 'annotation_class'):
            annotations = related_object.model._get_annotations('*')
            queryset = queryset.annotate(**annotations)
        return queryset

    def _optimize_queryset_prefetch_related(self, queryset, related_object):
        for field_type in related_object.model._meta.get_fields():
            if isinstance(field_type, ManyToManyField):
                queryset = queryset.prefetch_related(field_type.name)
        return queryset



class RelatedObjectPermissionMixin:
    """
    A mixin for RelatedObjectMixin that set permissions for retrieving related fields.
    """

    def get_permissions_for_object(self, related_object):
        permissions = self._get_related_object_option(related_object, 'permissions', [AllowAny])
        return [permission() for permission in permissions]

    def check_related_object_permission(self, obj, related_object_name):
        request = self.context.get('request')
        view = self.context.get('view')
        for permission in self.get_permissions_for_object(related_object_name):
            if not permission.has_object_permission(request, view, obj):
                raise PermissionDenied(
                    detail=f'You do not have permission to access the related object `{related_object_name}`'
                )
            if not permission.has_permission(request, view):
                raise PermissionDenied(
                    detail=f'You do not have permission to access the related object `{related_object_name}`'
                )


class RelatedObjectFilterMixin:
    """
    A mixin for RelatedObjectMixin that filter the related object queryset
    """

    def filter_related_object_query(self, queryset, related_object_name):
        related_objects_filter = self._get_related_object_option(related_object_name, 'filter')
        if related_objects_filter:
            queryset = queryset.filter(**related_objects_filter)
        return queryset.all()


class RelatedObjectMixin(
    RelatedObjectPermissionMixin,
    RelatedObjectFilterMixin,
    RelatedObjetsOptimizeMixin
):
    """
    A mixin for ModelSerializer that retrieve related object (foreign keys, generic relations, m2m) that will be
    returned in response data.
    """

    def _get_related_object_option(self, related_object, option_name, default=None):
        related_objects = self.get_related_objects()
        options = related_objects.get(related_object)
        return options.get(option_name, default)

    def get_related_objects(self):
        related_objects = getattr(self.Meta, 'related_objects', dict())
        return related_objects

    def get_related_object_serializer(self, related_object):
        serializer = self._get_related_object_option(related_object, 'serializer')
        if isinstance(serializer, str):
            serializer = import_string(serializer)
        return serializer

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        related_objects_fields = self.context.get('fields', dict())
        related_objects = self.get_related_objects()
        for related_object_name in related_objects.keys():
            fields = related_objects_fields.get(related_object_name)
            if fields:
                self.check_related_object_permission(instance, related_object_name)

                related_object = getattr(instance, related_object_name)
                Serializer = self.get_related_object_serializer(related_object_name)
                serializer_kwargs = {'fields': fields}

                if isinstance(related_object, Manager):
                    queryset = self.filter_related_object_query(related_object, related_object_name)
                    queryset = self.optimize_queryset(queryset, related_object)

                    paginator = PaginatorRelatedObject(
                        queryset=queryset,
                        related_object_name=related_object_name,
                        related_object_fields=fields,
                        request=self.context.get('request')
                    )

                    serializer_kwargs.update({'many': True})

                    page = paginator.paginate_queryset()
                    if page:
                        serializer = Serializer(page, **serializer_kwargs)
                        ret[related_object_name] = paginator.get_paginated_data(serializer.data)
                        continue
                    serializer = Serializer(queryset, **serializer_kwargs)
                    ret[related_object_name] = serializer.data
                else:
                    related_object = self.optimize_related_object(instance, related_object)
                    serializer = Serializer(related_object, **serializer_kwargs)
                    ret[related_object_name] = serializer.data
        return ret


class CreateAndUpdateOnlyFieldsMixin:
    """
    A mixin for ModelSerializer that allows fields that can be sent only in create methods or fields that only can be
    sent only in update methods.
    """

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if self.instance:
            create_only_fields = getattr(self.Meta, 'create_only_fields', tuple())
            for field in create_only_fields:
                ret.pop(field, None)
        else:
            update_only_fields = getattr(self.Meta, 'update_only_fields', tuple())
            for field in update_only_fields:
                ret.pop(field, None)
        return ret

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if hasattr(self.Meta, 'create_only_fields') and self.instance:
            for field in self.Meta.create_only_fields:
                extra_kwargs.setdefault(field, {}).update({'required': False})
        return extra_kwargs


class PermissionForFieldMixin:
    """
    A mixin for ModelSerializer that set permissions for performing actions using model's foreign keys fields.
    """

    def get_permissions_for_field(self, field):
        permissions_for_field = getattr(self.Meta, 'permissions_for_field', dict())
        for fields, permissions in permissions_for_field.items():
            if field in fields:
                return [permission() for permission in permissions]
        return [AllowAny()]

    def check_field_permission(self, field_name, obj):
        request = self.context.get('request')
        view = self.context.get('view')
        for permission in self.get_permissions_for_field(field_name):
            if not permission.has_object_permission(request, view, obj):
                raise PermissionDenied(
                    detail=f'You do not have permission to use `{field_name}` with this id'
                )

    def validate(self, attrs):
        permissions_for_field = getattr(self.Meta, 'permissions_for_field', dict())
        for fields in permissions_for_field:
            [self.check_field_permission(field, attrs[field]) for field in fields if field in attrs]
        return attrs


class DynamicModelFieldsMixin:
    """
    A mixin for ModelSerializer that takes an additional `fields` argument that controls which fields should be
    displayed.

    There are three field's types which return certain fields that are defined in ModelSerializer, types are:
    - @min - only the `basic` object's fields
    - @default - only the default object's fields
    - @all - all object's fields

    You can modify this fields as you want.
    """
    field_types = {'@min': 'min_fields', '@default': 'default_fields'}

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:

            if '@all' in fields:
                return

            for field in fields:
                if field in self.field_types:
                    field_values = getattr(self.Meta, self.field_types[field], tuple())
                    fields += field_values

            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class AnnotationFieldMixin:
    def get_fields(self):
        fields = super().get_fields()

        annotation_class = getattr(self.Meta.model, 'annotation_class', None)
        if annotation_class:
            fields.update(annotation_class._get_annotation_serializer_fields())

        return fields
