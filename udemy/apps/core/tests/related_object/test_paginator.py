from unittest.mock import patch

from django.test import TestCase, RequestFactory, override_settings
from django.urls import path

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from udemy.apps.core.mixins.view import RetrieveRelatedObjectMixin
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
            }
        }


factory = RequestFactory()
request = factory.get('/')


class ModelTestViewSet(RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = ModelTest.objects.all()
    serializer_class = ModelTestSerializer

    class Meta:
        model = ModelTest


urlpatterns = [
    path('test/<int:pk>/', ModelTestViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectPaginator(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='test')
        self.model_1 = ModelRelatedObject.objects.create(title='model 1', model_test=self.model_test)
        self.model_2 = ModelRelatedObject.objects.create(title='model 2', model_test=self.model_test)
        self.model_3 = ModelRelatedObject.objects.create(title='model 3', model_test=self.model_test)
        self.model_4 = ModelRelatedObject.objects.create(title='model 4', model_test=self.model_test)
        self.url = reverse('test-retrieve', kwargs={'pk': self.model_test.id})
        self.client = APIClient()

    @patch('udemy.apps.core.paginator.RELATED_OBJECT_PAGINATED_BY', 1)
    def test_related_objects_are_paginated(self):
        response = self.client.get(f'{self.url}?fields[model_related]=@all,page(2)')

        expected_response = {
            'id': self.model_test.id,
            'title': self.model_test.title,
            'model_related': {
                'count': 4,
                'next': f'http://testserver/test/{self.model_test.id}/?fields%5Bmodel_related%5D=%40all%2Cpage%283%29',
                'previous': f'http://testserver/test/{self.model_test.id}/?fields%5Bmodel_related%5D=%40all',
                'results': [{
                    'id': self.model_2.id,
                    'title': self.model_2.title,
                    'model_test': self.model_test.id
                }]
            }
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_response

    def test_setting_page_size(self):
        response = self.client.get(f'{self.url}?fields[model_related]=@all,page_size(2)')

        expected_response = {
            'id': self.model_test.id,
            'title': self.model_test.title,
            'model_related': {
                'count': 4,
                'next': f'http://testserver/test/{self.model_test.id}/?fields%5Bmodel_related%5D=%40all%2Cpage_size%282%29%2Cpage%282%29',
                'previous': None,
                'results': [
                    {
                        'id': self.model_1.id,
                        'title': self.model_1.title,
                        'model_test': self.model_test.id
                    },
                    {
                        'id': self.model_2.id,
                        'title': self.model_2.title,
                        'model_test': self.model_test.id
                    }
                ]
            }
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_response

    def test_404_for_invalid_page_size(self):
        response = self.client.get(f'{self.url}?fields[model_related]=@all,page_size(0)')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {'detail': 'Invalid page size for `model_related`.'}

    def test_404_for_invalid_page(self):
        response = self.client.get(f'{self.url}?fields[model_related]=@all,page(1000)')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {'detail': 'Invalid page for `model_related`.'}
