from django.test import TestCase

from udemy.apps.core.models import ModelTest, ModelRelatedObject
from udemy.apps.core.serializer import ModelSerializer


class RelatedObjectSerializer(ModelSerializer):
    class Meta:
        model = ModelRelatedObject
        fields = ('id', 'title', 'model_test')


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')
        related_objects = {
            'model_related': {
                'serializer': RelatedObjectSerializer,
                'many': True,
                'filter': {'title__startswith': 'test'}
            }
        }


class TestRelatedObjectFilter(TestCase):
    def test_related_object_filter(self):
        model_test = ModelTest.objects.create(title='test')
        model_1 = ModelRelatedObject.objects.create(title='test_', model_test=model_test)
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)
        model_2 = ModelRelatedObject.objects.create(title='test_', model_test=model_test)
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)

        serializer = ModelTestSerializer(fields=('id', 'title', 'model_related'),
                                         context={'related_objects': {'model_related': ['@all']}})
        data = serializer.to_representation(model_test)

        expected_data = {
            'id': model_test.id,
            'title': model_test.title,
            'model_related': [
                {
                    'id': model_1.id,
                    'title': model_1.title,
                    'model_test': model_test.id
                },
                {
                    'id': model_2.id,
                    'title': model_2.title,
                    'model_test': model_test.id
                }
            ]
        }

        assert data == expected_data

    def test_related_object_filter_without_match(self):
        model_test = ModelTest.objects.create(title='test')
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)
        ModelRelatedObject.objects.create(title='no_test', model_test=model_test)

        serializer = ModelTestSerializer(fields=('id', 'title', 'model_related'),
                                         context={'related_objects': {'model_related': ['@all']}})
        data = serializer.to_representation(model_test)

        expected_data = {
            'id': model_test.id,
            'title': model_test.title,
            'model_related': []
        }

        assert data == expected_data

    def test_related_object_filter_kwargs(self):
        serializer = ModelTestSerializer(context={'related_objects': {'model_related': ['@all']}})
        filter_kwargs = serializer._get_related_object_option('model_related', 'filter')

        assert filter_kwargs == {'title__startswith': 'test'}
