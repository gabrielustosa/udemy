from unittest.mock import patch

from django.test import TestCase, RequestFactory, override_settings
from django.urls import path
from rest_framework import status

from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from tests.factories.user import UserFactory

from udemy.apps.core.mixins.view import RetrieveRelatedObjectMixin
from udemy.apps.core.models import ModelTest, ModelRelatedObject
from udemy.apps.core.serializer import ModelSerializer


class FakePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, 'fake_permission')


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
                'serializer': ModelTestSerializer,
                'permissions': [FakePermission]
            }
        }


factory = RequestFactory()
request = factory.get('/')


class RelatedObjectViewSet(RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()
    serializer_class = RelatedObjectSerializer

    class Meta:
        model = ModelRelatedObject


urlpatterns = [
    path('test/<int:pk>/', RelatedObjectViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectPermissions(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_related_object_permission(self):
        model_test = ModelTest.objects.create(title='teste')
        related_object = ModelRelatedObject.objects.create(title='related_test', model_test=model_test)

        user = UserFactory()
        user.fake_permission = True
        self.client.force_authenticate(user)

        url = reverse('test-retrieve', kwargs={'pk': related_object.id})
        response = self.client.get(f'{url}?fields[model_test]=@all')

        expected_data = {
            'id': related_object.id,
            'model_test': {
                'id': model_test.id,
                'title': model_test.title
            },
            'title': related_object.title
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_related_object_permission_denied(self):
        model_test = ModelTest.objects.create(title='teste')
        related_object = ModelRelatedObject.objects.create(title='related_test', model_test=model_test)

        url = reverse('test-retrieve', kwargs={'pk': related_object.id})
        response = self.client.get(f'{url}?fields[model_test]=@all')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_permissions(self):
        model_test = ModelTest.objects.create(title='teste')
        related_object = ModelRelatedObject.objects.create(title='related_test', model_test=model_test)

        serializer = RelatedObjectSerializer(related_object)

        assert [p.__class__ for p in serializer.get_permissions_for_object('model_test')] == [FakePermission]

    def test_get_default_permissions(self):
        model_test = ModelTest.objects.create(title='teste')
        related_object = ModelRelatedObject.objects.create(title='related_test', model_test=model_test)

        default_related_objects = {'model_test': {'serializer': ModelTestSerializer}}
        with patch.object(RelatedObjectSerializer.Meta, 'related_objects', default_related_objects):
            serializer = RelatedObjectSerializer(related_object)

            assert [p.__class__ for p in serializer.get_permissions_for_object('model_test')] == [AllowAny]
