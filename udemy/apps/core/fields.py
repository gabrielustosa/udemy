from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class GenericRelatedField(serializers.Field):
    """
    Represents a generic relation / foreign key. It's actually more of a wrapper, that delegates the logic to registered
    serializers based on the `Model` class.
    """
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
            raise serializers.ValidationError(e)
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
        raise serializers.ValidationError(self.error_messages['no_model_match'])

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


class AnnotationDictField(serializers.Field):

    def __init__(self, *args, **kwargs):
        self.children = kwargs.pop('children')
        kwargs['read_only'] = True

        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return {
            child.annotation_name: child.get_attribute(instance)
            for child in self.children
        }

    def to_representation(self, value):
        return {
            key: child.to_representation(val) if val is not None else None
            for child in self.children
            for key, val in value.items()
        }


class AnnotationField(serializers.Field):

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child')
        self.annotation_name = kwargs.pop('annotation_name', None)
        kwargs['read_only'] = True

        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return getattr(instance, self.annotation_name, None)

    def to_representation(self, value):
        return self.child.to_representation(value)


class RelatedObjectListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        self.filter = kwargs.pop('filter', None)
        self.paginator = kwargs.pop('paginator', None)

        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        if isinstance(data, Manager):
            if self.filter:
                data = data.filter(**self.filter)
            iterable = data.all()

            if self.paginator:
                iterable = self.paginator.paginate_queryset(iterable)
        else:
            iterable = data

        ret = [self.child.to_representation(item) for item in iterable]

        if self.paginator and self.paginator.num_pages > 1:
            return self.paginator.get_paginated_data(ret)

        return ret
