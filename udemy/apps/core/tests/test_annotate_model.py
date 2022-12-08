from django.db.models import Value
from django.test import TestCase, RequestFactory, override_settings
from django.urls import path

from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from tests.factories.lesson import LessonFactory
from udemy.apps.core.mixins.view import AnnotateModelMixin, DynamicFieldViewMixin
from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.lesson.serializer import LessonSerializer


class ModelTestSerializer(ModelSerializer):

    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'test_field', 'custom_field')


class AnnotateModelViewSet(AnnotateModelMixin, DynamicFieldViewMixin, ModelViewSet):
    queryset = ModelTest.objects.all()
    serializer_class = ModelTestSerializer

    class Meta:
        model = ModelTest


factory = RequestFactory()
request = factory.get('/')

urlpatterns = [
    path('test/<int:pk>/', AnnotateModelViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestAnnotateView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_serializer_method_fields(self):
        view = AnnotateModelViewSet(request=request)
        request.query_params = {'fields': 'test_field,id,title'}

        assert view.get_annotation_fields() == {'test_field'}

    def test_get_serializer_method_fields_without_fields_param(self):
        view = AnnotateModelViewSet(request=request)
        request.query_params = {}

        assert view.get_annotation_fields() == {'test_field', 'custom_field'}

    def test_retrieve_annotation_method(self):
        model_test = ModelTest.objects.create(title='test')

        url = reverse('test-retrieve', kwargs={'pk': model_test.id})
        response = self.client.get(url)

        expected_data = {
            'id': model_test.id,
            'title': model_test.title,
            'test_field': 'test field',
            'custom_field': 'custom field',
        }

        assert response.data == expected_data

    def test_retrieve_annotation_method_with_one_field(self):
        model_test = ModelTest.objects.create(title='test')

        url = reverse('test-retrieve', kwargs={'pk': model_test.id})
        response = self.client.get(f'{url}?fields=test_field')

        expected_data = {
            'test_field': 'test field'
        }

        assert response.data == expected_data


class TestAnnotateModel(TestCase):
    def test_get_model_annotations(self):
        annotations = ModelTest.get_annotations('test_field', 'custom_field')

        assert annotations == {'_custom_field': Value('custom field'), '_test_field': Value('test field')}
