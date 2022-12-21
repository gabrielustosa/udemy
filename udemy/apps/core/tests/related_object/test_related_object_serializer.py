from django.test import TestCase

from udemy.apps.core.models import ModelTest, ModelRelatedObject
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'model_related')
        related_objects = dict(
            model_related=dict(
                serializer=f'{__name__}.RelatedObjectSerializer',
                many=True,
            )
        )


class RelatedObjectSerializer(ModelSerializer):
    class Meta:
        model = ModelRelatedObject
        fields = ('id', 'title', 'model_test', 'models_tests')
        related_objects = dict(
            model_test=dict(
                serializer=ModelTestSerializer
            ),
            models_tests=dict(
                serializer=ModelTestSerializer,
                many=True,
            )
        )


class TestRelatedObjectSerializer(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)
        self.related_object.models_tests.add(self.model_test)

    def test_related_object_serializer_foreign(self):
        context = {'related_objects': {'model_test': ['id', 'title']}}
        related_serializer = RelatedObjectSerializer(self.related_object, context=context)

        expected_data = {
            'id': self.related_object.id,
            'model_test': {
                'id': self.model_test.id,
                'title': self.model_test.title
            },
            'title': self.related_object.title,
            'models_tests': [self.model_test.id]
        }

        assert related_serializer.data == expected_data

    def test_related_object_serializer_many_to_many(self):
        context = {'related_objects': {'models_tests': ['id', 'title']}}
        related_serializer = RelatedObjectSerializer(self.related_object, context=context)

        expected_data = {
            'id': self.related_object.id,
            'model_test': self.model_test.id,
            'title': self.related_object.title,
            'models_tests': [
                {
                    'id': self.model_test.id,
                    'title': self.model_test.title
                }
            ]
        }

        assert related_serializer.data == expected_data

    def test_related_object_serializer_many_to_one(self):
        context = {'related_objects': {'model_related': ['id', 'title']}}
        related_serializer = ModelTestSerializer(self.model_test, fields=('id', 'model_related'), context=context)

        expected_data = {
            'id': self.model_test.id,
            'model_related': [
                {
                    'id': self.related_object.id,
                    'title': self.related_object.title
                }
            ]
        }

        assert related_serializer.data == expected_data

    def test_related_object_serializer_with_two_related_objects(self):
        context = {'related_objects': {'models_tests': ['id', 'title'], 'model_test': ['id', 'title']}}
        related_serializer = RelatedObjectSerializer(self.related_object, context=context)

        expected_data = {
            'id': self.related_object.id,
            'model_test': {
                'id': self.model_test.id,
                'title': self.model_test.title
            },
            'title': self.related_object.title,
            'models_tests': [
                {
                    'id': self.model_test.id,
                    'title': self.model_test.title
                }
            ]
        }

        assert related_serializer.data == expected_data

    def test_related_object_serializer_with_invalid_related_object(self):
        context = {'related_objects': {'invalid_model': ['id', 'title']}}
        related_serializer = RelatedObjectSerializer(self.related_object, context=context)

        expected_data = {
            'id': self.related_object.id,
            'model_test': self.model_test.id,
            'title': self.related_object.title,
            'models_tests': [self.model_test.id]
        }

        assert related_serializer.data == expected_data
