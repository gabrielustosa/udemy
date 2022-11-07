from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
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


class ActionGenericField(s.Field):
    def __init__(self, allowed_models, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_models = allowed_models

    def get_model_by_name(self, name):
        models = {model.__name__.lower(): model for model in self.allowed_models.keys()}
        return models.get(name)

    def to_internal_value(self, data):
        if 'model' not in data:
            raise s.ValidationError('You must refer a model to this action.')
        if 'object_id' not in data:
            raise s.ValidationError('You must provide the object id.')

        Model = self.get_model_by_name(data['model'])
        if not Model:
            raise s.ValidationError('Invalid model - model not found.')

        try:
            content_object = Model.objects.get(id=data['object_id'])
        except ObjectDoesNotExist:
            raise s.ValidationError('Invalid id - object not found.')

        return content_object

    def to_representation(self, value):
        serializer = self.allowed_models[value.__class__]
        return serializer.to_representation(instance=value)
