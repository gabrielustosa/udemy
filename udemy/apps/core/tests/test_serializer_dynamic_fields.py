from django.test import TestCase
from rest_framework import serializers

from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    custom_field = serializers.SerializerMethodField()

    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'custom_field')
        min_fields = ('custom_field',)
        default_fields = ('id', 'title')

    def get_custom_field(self, instance):
        return f'custom field {instance.id}'

class SerializerDynamicFieldsTests(TestCase):
    def test_dynamic_fields(self):
        model_test = ModelTest.objects.create(title='test')

        serializer = ModelTestSerializer(fields=('id', 'custom_field'))
        data = serializer.to_representation(model_test)

        assert data == {'id': model_test.id, 'custom_field': f'custom field {model_test.id}'}

    def test_min_fields(self):
        model_test = ModelTest.objects.create(title='test')

        serializer = ModelTestSerializer(fields=('@min',))
        data = serializer.to_representation(model_test)

        assert data == {'custom_field': f'custom field {model_test.id}'}

    def test_default_fields(self):
        model_test = ModelTest.objects.create(title='test')

        serializer = ModelTestSerializer(fields=('@default',))
        data = serializer.to_representation(model_test)

        assert data == {'id': model_test.id, 'title': model_test.title}

    def test_all_fields(self):
        model_test = ModelTest.objects.create(title='test')

        serializer = ModelTestSerializer(fields=('@all',))
        data = serializer.to_representation(model_test)

        assert data == {'id': model_test.id, 'title': model_test.title, 'custom_field': f'custom field {model_test.id}'}
