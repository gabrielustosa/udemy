from django.test import TestCase

from udemy.apps.core.models import ModelTest, ModelRelatedObject
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')


class RelatedObjectSerializer(ModelSerializer):
    class Meta:
        model = ModelRelatedObject
        fields = '__all__'
        related_objects = {
            'model_test': {
                'serializer': ModelTestSerializer
            }
        }


class RelatedObjectSerializerString(ModelSerializer):
    class Meta:
        model = ModelRelatedObject
        fields = '__all__'
        related_objects = {
            'model_test': {
                'serializer': f'{__name__}.RelatedObjectSerializerString'
            }
        }


class TestRelatedObjectSerializer(TestCase):

    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)
    def test_related_object_serialize(self):
        related_serializer = RelatedObjectSerializer(self.related_object, context={'fields': {'model_test': '@all'}})

        expected_data = {
            'id': self.related_object.id,
            'model_test': {
                'id': self.model_test.id,
                'title': self.model_test.title
            },
            'title': self.related_object.title
        }

        assert related_serializer.data == expected_data

    def test_related_object_serializer_with_invalid_related_object(self):
        related_serializer = RelatedObjectSerializer(self.related_object, context={'fields': {'invalid_model': '@all'}})

        expected_data = {
            'id': self.related_object.id,
            'model_test': self.model_test.id,
            'title': self.related_object.title
        }

        assert related_serializer.data == expected_data

    def test_get_related_objects(self):
        related_serializer = RelatedObjectSerializer(self.related_object, context={'fields': {'model_test': '@all'}})

        expected_objects = {
            'model_test': {
                'serializer': ModelTestSerializer
            },
        }

        assert related_serializer.get_related_objects() == expected_objects

    def test_get_related_object_serializer(self):
        related_serializer = RelatedObjectSerializer(self.related_object, context={'fields': {'model_test': '@all'}})

        Serializer = related_serializer.get_related_object_serializer('model_test')

        assert Serializer == ModelTestSerializer

    def test_get_related_object_serializer_from_string(self):
        related_serializer = RelatedObjectSerializerString(self.related_object, context={'fields': {'model_test': '@all'}})

        Serializer = related_serializer.get_related_object_serializer('model_test')

        assert Serializer == RelatedObjectSerializerString
