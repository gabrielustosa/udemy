from django.db.models import Manager

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny

from udemy.apps.core.paginator import PaginatorRelatedObject
from utils.module import get_class_from_module


class RelatedObjectPermissionMixin:
    """
    A mixin for RelatedObjectMixin that set permissions for retrieving related fields.
    """

    def get_permissions_for_object(self, related_object):
        related_objects_permissions = getattr(self.Meta, 'related_objects_permissions', dict())
        for related_objects, permissions in related_objects_permissions.items():
            if related_object in related_objects:
                return [permission() for permission in permissions]
        return [AllowAny()]

    def check_related_object_permission(self, obj, related_object_name):
        request = self.context.get('request')
        view = self.context.get('view')
        for permission in self.get_permissions_for_object(related_object_name):
            if not permission.has_object_permission(request, view, obj):
                raise PermissionDenied(
                    detail=f'You do not have permission to access the related object `{related_object_name}`'
                )


class RelatedObjectFilterMixin:
    """
    A mixin for RelatedObjectMixin that filter the related object (if its object is a queryset)
    """

    def get_related_objects_filters(self):
        return getattr(self.Meta, 'related_objects_filters', {})

    def filter_related_object_query(self, obj, related_object_name):
        related_objects_filters = self.get_related_objects_filters()
        for related_object, filter_kwargs in related_objects_filters.items():
            if related_object == related_object_name:
                obj = obj.filter(**filter_kwargs)
        return obj.order_by('id').all()


class RelatedObjectMixin(
    RelatedObjectPermissionMixin,
    RelatedObjectFilterMixin,
):
    """
    A mixin for ModelSerializer that retrieve related object (foreign keys, generic relations, m2m) that will be
    returned in response data.
    """

    def get_related_object_fields(self, related_object_name):
        related_objects_fields = self.context.get('fields', {})
        return related_objects_fields.get(related_object_name)

    def get_related_objects(self):
        related_objects = getattr(self.Meta, 'related_objects', {})
        for related_object, serializer in related_objects.items():
            if isinstance(serializer, tuple):
                module_name, class_name = serializer
                related_objects[related_object] = get_class_from_module(module_name, class_name)
        return related_objects.items()

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        related_objects = self.get_related_objects()
        for related_object_name, Serializer in related_objects:
            fields = self.get_related_object_fields(related_object_name)
            if fields:
                self.check_related_object_permission(instance, related_object_name)

                related_object = getattr(instance, related_object_name)

                if isinstance(related_object, Manager):
                    queryset = self.filter_related_object_query(related_object, related_object_name)

                    paginator = PaginatorRelatedObject(
                        queryset=queryset,
                        related_object_name=related_object_name,
                        related_object_fields=fields,
                        request=self.context.get('request')
                    )

                    page = paginator.paginate_queryset()
                    if paginator.num_pages > 1:
                        serializer = Serializer(page, fields=fields, many=True)
                        ret[related_object_name] = paginator.get_paginated_data(serializer.data)
                        continue
                    serializer = Serializer(queryset, fields=fields, many=True)
                    ret[related_object_name] = serializer.data
                else:
                    serializer = Serializer(related_object, fields=fields)
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
            [ret.pop(field) for field in create_only_fields if field in ret]
        else:
            update_only_fields = getattr(self.Meta, 'update_only_fields', tuple())
            [ret.pop(field) for field in update_only_fields if field in ret]
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
