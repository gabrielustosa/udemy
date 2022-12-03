from django.urls import path
from django.test import TestCase, override_settings, RequestFactory

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from udemy.apps.core.mixins.view import DynamicFieldViewMixin
from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class ModelTestSerializer(ModelSerializer):
    custom_field = serializers.SerializerMethodField()

    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'custom_field')

    def get_custom_field(self, instance):
        return f'custom field {instance.id}'


class ModelTestViewSet(DynamicFieldViewMixin, ModelViewSet):
    queryset = ModelTest.objects.all()
    serializer_class = ModelTestSerializer

    class Meta:
        model = ModelTest


urlpatterns = [
    path('test/<int:pk>/', ModelTestViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]

factory = RequestFactory()
request = factory.get('/')


@override_settings(ROOT_URLCONF=__name__)
class TestDynamicFieldsView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_dynamic_view_fields(self):
        model_test = ModelTest.objects.create(title='teste')

        url = reverse('test-retrieve', kwargs={'pk': model_test.id})
        response = self.client.get(f'{url}?fields=custom_field')

        assert response.data == {'custom_field': f'custom field {model_test.id}'}
