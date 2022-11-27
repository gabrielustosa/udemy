from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers as rest_serializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny

from utils.module import get_class_from_module


class GenericField(rest_serializer.Field):
    default_error_messages = {
        'no_model_match': _('Invalid model - model not available.'),
        'no_url_match': _('Invalid hyperlink - No URL match'),
        'incorrect_url_match': _(
            'Invalid hyperlink - view name not available'),
    }

    def __init__(self, serializers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializers = serializers

        for serializer in serializers.values():
            if serializer.source is not None:
                msg = '{}() cannot be re-used. Create a new instance.'
                raise RuntimeError(msg.format(type(serializer).__name__))
            serializer.bind('', self)

    def to_internal_value(self, data):
        try:
            serializer, Model = self.get_serializer_for_data(data)
        except ImproperlyConfigured as e:
            raise rest_serializer.ValidationError(e)
        ret = serializer.to_internal_value(data)

        model_object = Model.objects.create(**ret)

        return model_object

    def to_representation(self, instance):
        serializer = self.get_serializer_for_instance(instance)
        return serializer.to_representation(instance)

    def get_serializer_for_instance(self, instance):
        for klass in instance.__class__.mro():
            if klass in self.serializers:
                return self.serializers[klass]
        raise rest_serializer.ValidationError(self.error_messages['no_model_match'])

    def get_serializer_for_data(self, value):
        serializer = model = None
        for Model, model_serializer in self.serializers.items():
            try:
                result = model_serializer.to_internal_value(value)
                if bool(result):
                    serializer = model_serializer
                    model = Model
            except Exception:
                pass
        return serializer, model


class DynamicModelFieldsMixin:
    """
    A mixin for ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.

    There are three types of field which return certain fields that are defined in
    ModelSerializer, the default types are:
    - @min - only the `basic` object's fields
    - @default - only the default object's fields
    - @all - all object's fields
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


class RelatedObjectMixin:
    """
    A mixin for ModelSerializer that retrieve related object (foreign keys, generic relations, m2m)
    that will be returned in response data.
    """

    def get_permissions_for_object(self, related_object):
        related_objects_permissions = getattr(self.Meta, 'related_objects_permissions', dict())
        for related_objects, permissions in related_objects_permissions.items():
            if related_object in related_objects:
                return [permission() for permission in permissions]
        return [AllowAny()]

    def get_related_fields(self):
        related_objects = getattr(self.Meta, 'related_objects', {})
        for related_object, serializer in related_objects.items():
            if isinstance(serializer, tuple):
                module_name, class_name = serializer
                related_objects[related_object] = get_class_from_module(module_name, class_name)
        return related_objects.items()

    def get_related_objects_filters(self):
        return getattr(self.Meta, 'related_objects_filters', {})

    def check_related_object_permission(self, related_object):
        request = self.context.get('request')
        view = self.context.get('view')
        for permission in self.get_permissions_for_object(related_object):
            if not permission.has_permission(request, view):
                raise PermissionDenied(
                    detail=f'You do not have permission to access the related object `{related_object}`'
                )

    def filter_related_object_query(self, obj, related_object_name):
        obj = obj.all()
        related_objects_filters = self.get_related_objects_filters()
        for related_object, filter_kwargs in related_objects_filters.items():
            if related_object == related_object_name:
                obj = obj.filter(**filter_kwargs)
        return obj

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        related_objects_fields = self.context.get('fields', {})
        related_objects = self.get_related_fields()
        for related_object, serializer in related_objects:
            fields = related_objects_fields.get(related_object)
            if fields:
                self.check_related_object_permission(related_object)

                serializer_options = {'fields': fields}
                obj = getattr(instance, related_object)

                queryset_all = getattr(obj, 'all', None)
                if queryset_all and callable(queryset_all):
                    serializer_options.update({'many': True})
                    obj = self.filter_related_object_query(obj, related_object)

                serializer = serializer(obj, **serializer_options)
                ret[related_object] = serializer.data
        return ret


class CreateAndUpdateOnlyFieldsMixin:
    """
    A mixin for ModelSerializer that allows fields that can be sent only in create methods or
    fields that only can be sent only in update methods.
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
    A mixin for ModelSerializer that set permissions for performing actions using
    model's foreign keys fields.
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


class ModelSerializer(
    DynamicModelFieldsMixin,
    RelatedObjectMixin,
    CreateAndUpdateOnlyFieldsMixin,
    PermissionForFieldMixin,
    rest_serializer.ModelSerializer
):
    """
    Custom ModelSerializer
    """
