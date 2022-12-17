from django.test import TestCase, override_settings
from django.urls import path
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins.view import RelatedObjectViewMixin
from udemy.apps.core.models import ModelTest, ModelRelatedObject
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title')
        related_objects = dict(
            model_related=dict(
                serializer=f'{__name__}.RelatedObjectSerializer',
                many=True,
            )
        )


class RelatedObjectSerializer(ModelSerializer):
    class Meta:
        model = ModelRelatedObject
        fields = ('id', 'title')
        related_objects = dict(
            model_test=dict(
                serializer=ModelTestSerializer
            ),
            models_tests=dict(
                serializer=ModelTestSerializer,
                many=True,
            )
        )


class RelatedObjectViewSet(RelatedObjectViewMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()
    serializer_class = RelatedObjectSerializer


urlpatterns = [
    path('test/<int:pk>/', RelatedObjectViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectAnnotations(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)

    def test_related_object_annotations_dict(self):
        context = {'related_fields': {'model_test': ['test_field', 'custom_field']}}
        related_object = ModelRelatedObject.objects.get(id=self.related_object.id)

        serializer = RelatedObjectSerializer(related_object, context=context)
        expected_annotations = ModelTest.annotation_class.get_annotations(
            'test_field', 'custom_field', additional_path='model_test'
        )

        assert serializer.related_objects_annotations['model_test'] == expected_annotations

    def test_related_object_annotations(self):
        url = reverse('test-retrieve', kwargs={'pk': self.related_object.id})
        response = self.client.get(f'{url}?fields[model_test]=test_field,custom_field')

        expected_annotations = {
            'test_field': 'model_test__test field',
            'custom_field': {
                'test_1': 0,
                'test_2': 0,
                'test_3': 0
            }
        }

        assert response.data['model_test'] == expected_annotations
