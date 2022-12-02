from django.test import TestCase, RequestFactory, override_settings
from django.urls import path
from rest_framework import status

from rest_framework.permissions import BasePermission
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
        permissions_for_field = {
            ('model_test',): [FakePermission]
        }


factory = RequestFactory()
request = factory.get('/')


class RelatedObjectViewSet(RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()
    serializer_class = RelatedObjectSerializer

    class Meta:
        model = ModelRelatedObject


urlpatterns = [
    path('test/', RelatedObjectViewSet.as_view({'post': 'create'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestPermissionForField(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_permission_for_field(self):
        model_test = ModelTest.objects.create(title='teste')

        user = UserFactory()
        user.fake_permission = True
        self.client.force_authenticate(user)

        url = reverse('test-retrieve')
        response = self.client.post(url, {'title': 'a', 'model_test': model_test.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_denied(self):
        model_test = ModelTest.objects.create(title='teste')

        url = reverse('test-retrieve')
        response = self.client.post(url, {'title': 'a', 'model_test': model_test.id})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {'detail': 'You do not have permission to use `model_test` with this id'}

    def test_get_permission_for_field(self):
        permissions = RelatedObjectSerializer().get_permissions_for_field('model_test')
        assert [p.__class__ for p in permissions] == [FakePermission]
