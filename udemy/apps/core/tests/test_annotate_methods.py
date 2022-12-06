from django.db.models import Value
from django.test import TestCase, RequestFactory, override_settings
from django.urls import path

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from udemy.apps.core.mixins.view import AnnotateMethodsMixin, DynamicFieldViewMixin
from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    test_field = serializers.SerializerMethodField()
    custom_field = serializers.SerializerMethodField()

    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'test_field', 'custom_field')

    def get_test_field(self, instance):
        return instance.test_field

    def get_custom_field(self, instance):
        return f'{instance.id} test'


class AnnotateMethodViewSet(AnnotateMethodsMixin, DynamicFieldViewMixin, ModelViewSet):
    queryset = ModelTest.objects.all()
    serializer_class = ModelTestSerializer

    class Meta:
        model = ModelTest


factory = RequestFactory()
request = factory.get('/')

urlpatterns = [
    path('test/<int:pk>/', AnnotateMethodViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestAnnotateMethods(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_serializer_method_fields(self):
        view = AnnotateMethodViewSet(request=request)
        request.query_params = {'fields': 'test_field,id,title'}

        assert view.get_serializer_method_fields() == ['test_field']

    def test_get_serializer_method_fields_without_fields_param(self):
        view = AnnotateMethodViewSet(request=request)
        request.query_params = {}

        assert view.get_serializer_method_fields() == ['test_field', 'custom_field']

    def test_get_model_annotation(self):
        view = AnnotateMethodViewSet(request=request)

        annotation = view.get_model_annotation('test_field')

        assert annotation == {'test_field': Value('Test Value')}

    def test_get_model_annotation_without_annotation_def(self):
        view = AnnotateMethodViewSet(request=request)

        annotation = view.get_model_annotation('custom_field')

        assert annotation is None

    def test_retrieve_annotation_method(self):
        model_test = ModelTest.objects.create(title='test')

        url = reverse('test-retrieve', kwargs={'pk': model_test.id})
        response = self.client.get(url)

        expected_data = {
            'id': model_test.id,
            'title': model_test.title,
            'test_field': 'Test Value',
            'custom_field': f'{model_test.id} test'
        }

        assert response.data == expected_data

    def test_retrieve_annotation_method_with_one_field(self):
        model_test = ModelTest.objects.create(title='test')

        url = reverse('test-retrieve', kwargs={'pk': model_test.id})
        response = self.client.get(f'{url}?fields=test_field')

        expected_data = {
            'test_field': 'Test Value'
        }

        assert response.data == expected_data
