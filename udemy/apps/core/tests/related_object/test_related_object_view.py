from django.test import TestCase, RequestFactory, override_settings
from django.urls import path
from rest_framework.reverse import reverse

from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins.view import RelatedObjectViewMixin
from udemy.apps.core.models import ModelRelatedObject, ModelTest
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
    serializer_class = RelatedObjectSerializer
    queryset = ModelRelatedObject.objects.all()


class ModelObjectViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = ModelTestSerializer
    queryset = ModelTest.objects.all()


factory = RequestFactory()
request = factory.get('/')

urlpatterns = [
    path('related/<int:pk>/', RelatedObjectViewSet.as_view({'get': 'retrieve'}), name='related-retrieve'),
    path('test/<int:pk>/', ModelObjectViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectView(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)
        self.related_object.models_tests.add(self.model_test)

    def test_related_fields_retrieve(self):
        view = RelatedObjectViewSet(request=request)
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        assert view.related_fields == {'model_test': ['id', 'name']}

    def test_fields_in_serializer_context(self):
        view = RelatedObjectViewSet(request=request)
        view.format_kwarg = None
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        assert view.get_serializer_context()['related_fields'] == {'model_test': ['id', 'name']}

    def test_related_object_foreign_key_optimization(self):
        url = reverse('related-retrieve', kwargs={'pk': self.related_object.id})

        with self.assertNumQueries(1):
            self.client.get(f'{url}?fields[model_test]=@all')

    def test_related_object_many_to_many_optimization(self):
        url = reverse('related-retrieve', kwargs={'pk': self.related_object.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[models_tests]=@all')

    def test_related_object_many_to_one_optimization(self):
        url = reverse('test-retrieve', kwargs={'pk': self.model_test.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[model_related]=@all')
