from django.test import TestCase, override_settings
from django.urls import path

from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from tests.factories.user import UserFactory

from udemy.apps.core.mixins.view import RelatedObjectViewMixin, DynamicFieldViewMixin
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
        fields = ('id', 'title', 'model_test')
        related_objects = {
            'model_test': {
                'serializer': ModelTestSerializer,
                'permissions': [FakePermission]
            }
        }


class RelatedObjectViewSet(RelatedObjectViewMixin, DynamicFieldViewMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()
    serializer_class = RelatedObjectSerializer

    class Meta:
        model = ModelRelatedObject


urlpatterns = [
    path('test/<int:pk>/', RelatedObjectViewSet.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectPermission(TestCase):
    def setUp(self):
        self.model_test = ModelTest.objects.create(title='teste')
        self.related_object = ModelRelatedObject.objects.create(title='related_test', model_test=self.model_test)
        self.client = APIClient()

    def test_related_object_permission(self):
        user = UserFactory()
        user.fake_permission = True
        self.client.force_authenticate(user)

        url = reverse('test-retrieve', kwargs={'pk': self.related_object.id})
        response = self.client.get(f'{url}?fields[model_test]=id,title&fields=id,title,model_test')

        expected_data = {
            'id': self.related_object.id,
            'model_test': {
                'id': self.model_test.id,
                'title': self.model_test.title
            },
            'title': self.related_object.title
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_related_object_permission_denied(self):
        url = reverse('test-retrieve', kwargs={'pk': self.related_object.id})
        response = self.client.get(f'{url}?fields[model_test]=@all')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {'detail': 'You do not have permission to access the related object `model_test`'}
