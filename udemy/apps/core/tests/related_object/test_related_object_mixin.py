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


class TestRelatedObjectMixin(TestCase):

    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)

    def test_get_related_objects(self):
        related_serializer = RelatedObjectSerializer(self.related_object)

        expected_objects = {
            'model_test': {
                'serializer': ModelTestSerializer
            },
            'models_tests': {
                'serializer': ModelTestSerializer,
                'many': True,
            }
        }

        assert related_serializer.related_objects() == expected_objects

    def test_get_related_object_serializer(self):
        test_serializer = RelatedObjectSerializer(self.related_object)

        Serializer = test_serializer.get_related_object_serializer('model_test')

        assert Serializer == ModelTestSerializer

    def test_get_related_object_serializer_from_string(self):
        test_serializer = ModelTestSerializer(self.model_test)

        Serializer = test_serializer.get_related_object_serializer('model_related')

        assert Serializer == RelatedObjectSerializer

    def test_related_objects_fields(self):
        context = {
            'related_fields': {
                'models_tests': ['id', 'title'], 'model_test': ['id', 'title'], 'invalid_model': ['id', 'name']
            }
        }
        test_serializer = RelatedObjectSerializer(self.related_object, context=context)

        expected_related_objects_fields = {
            'models_tests': ['id', 'title'],
            'model_test': ['id', 'title']
        }

        assert test_serializer.related_objects_fields == expected_related_objects_fields

    def test_get_related_object_model(self):
        test_serializer = RelatedObjectSerializer(self.related_object)

        assert test_serializer.get_related_object_model('model_test') == ModelTest

    def test_related_object_is_prefetch(self):
        test_serializer = RelatedObjectSerializer(self.related_object)

        assert test_serializer.related_object_is_prefetch('model_test') == False
        assert test_serializer.related_object_is_prefetch('models_tests') == True
