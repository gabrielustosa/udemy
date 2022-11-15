from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers as s


class GenericField(s.Field):
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
            raise s.ValidationError(e)
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
        raise s.ValidationError(self.error_messages['no_model_match'])

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


class ModelSerializer(s.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        related_objects_fields = self.context.get('fields')
        if hasattr(self.Meta, 'related_objects') and related_objects_fields:
            for related_object, serializer in self.Meta.related_objects.items():
                fields = related_objects_fields.get(related_object)
                if fields:
                    obj = getattr(instance, related_object)
                    serializer = serializer(obj, fields=fields)
                    ret[related_object] = serializer.data
        return ret
