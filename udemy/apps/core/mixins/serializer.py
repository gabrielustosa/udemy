from django.core.exceptions import FieldError
from django.db.models import Manager, F
from django.utils.module_loading import import_string

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny

from udemy.apps.core.paginator import PaginatorRelatedObject


class RelatedObjectExpandedFieldMixin:
    """
    A mixin for RelatedObjectMixin that allow access to object's field of related object.

    Example:
        https://example.com/fields[related_object]=object__title
    """

    def annotate_expanded_m2m_fields(self, related_object_name, queryset):
        expanded_fields = self.get_expanded_m2m_fields(related_object_name)

        to_remove = []
        for field in expanded_fields:
            try:
                queryset = queryset.annotate(**{field: F(field)})
            except FieldError:
                to_remove.append(field)

        [expanded_fields.remove(field) for field in to_remove]

        return queryset

    def get_annotated_expanded_foreign_fields(self, instance, related_object_name):
        expanded_fields = self.get_expanded_foreign_fields(related_object_name)

        result = dict()
        for field in expanded_fields:
            result[field] = getattr(instance, f'{related_object_name}_{field}')
        return result

    def get_expanded_foreign_fields(self, related_object_name):
        expanded_foreign_fields = self.context.get('expanded_foreign_fields', dict())
        return expanded_foreign_fields.get(related_object_name, [])

    def get_expanded_m2m_fields(self, related_object_name):
        expanded_m2m_fields = self.context.get('expanded_m2m_fields', dict())
        return expanded_m2m_fields.get(related_object_name, [])


class RelatedObjectPermissionMixin:
    """
    A mixin for RelatedObjectMixin that set permissions for retrieving related fields.
    """

    def get_permissions_for_object(self, related_object):
        permissions = self.get_related_object_option(related_object, 'permissions', [AllowAny])
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
        related_objects_filter = self.get_related_object_option(related_object_name, 'filter')
        if related_objects_filter:
            queryset = queryset.filter(**related_objects_filter)
        return queryset.order_by('id')


class RelatedObjectMixin(
    RelatedObjectPermissionMixin,
    RelatedObjectFilterMixin,
    RelatedObjectExpandedFieldMixin,
):
    """
    A mixin for ModelSerializer that retrieve related object (foreign keys, generic relations, m2m) that will be
    returned in response data.
    """

    def get_related_objects(self):
        related_objects = getattr(self.Meta, 'related_objects', dict())
        return related_objects

    def get_related_object_option(self, related_object, option_name, default=None):
        related_objects = self.get_related_objects()
        options = related_objects.get(related_object)
        return options.get(option_name, default)

    def get_related_object_serializer(self, related_object):
        serializer = self.get_related_object_option(related_object, 'serializer')
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
                    queryset = self.annotate_expanded_m2m_fields(related_object_name, queryset)

                    paginator = PaginatorRelatedObject(
                        queryset=queryset,
                        related_object_name=related_object_name,
                        related_object_fields=fields,
                        request=self.context.get('request')
                    )

                    expanded_fields = self.get_expanded_m2m_fields(related_object_name)
                    serializer_kwargs.update({'many': True, 'context': {'expanded_m2m': expanded_fields}})

                    page = paginator.paginate_queryset()
                    if page:
                        serializer = Serializer(page, **serializer_kwargs)
                        ret[related_object_name] = paginator.get_paginated_data(serializer.data)
                        continue
                    serializer = Serializer(queryset, **serializer_kwargs)
                    ret[related_object_name] = serializer.data
                else:
                    expanded_fields = self.get_annotated_expanded_foreign_fields(instance, related_object_name)
                    serializer_kwargs.update({'context': {'expanded_foreign': expanded_fields}})
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


class ExpandedFieldMixin:
    """
    A mixin for ModelSerializer that add to the response expanded fields annotated by RelatedObject
    """

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        expanded_foreign = self.context.get('expanded_foreign', dict())
        for field_name, value in expanded_foreign.items():
            ret[field_name] = value

        expanded_m2m = self.context.get('expanded_m2m', list())
        for field_name in expanded_m2m:
            ret[field_name] = getattr(instance, field_name)

        return ret


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
