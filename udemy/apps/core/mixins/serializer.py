from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny


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
            fields.update(annotation_class.get_annotation_serializer_fields())

        return fields

