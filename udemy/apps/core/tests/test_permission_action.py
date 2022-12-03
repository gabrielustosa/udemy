from django.test import TestCase

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins.view import ActionPermissionMixin
from udemy.apps.core.models import ModelRelatedObject


class RelatedObjectViewSet(ActionPermissionMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()
    permission_classes_by_action = {
        ('retrieve',): [AllowAny],
        ('default',): [IsAuthenticated]
    }

    class Meta:
        model = ModelRelatedObject


class TestActionPermission(TestCase):
    def test_get_permission_by_action(self):
        view = RelatedObjectViewSet()

        assert [p.__class__ for p in view.get_permissions_by_action('retrieve')] == [AllowAny]

    def test_get_permissions(self):
        view = RelatedObjectViewSet()
        view.action = 'retrieve'

        assert [p.__class__ for p in view.get_permissions()] == [AllowAny]

    def test_get_default_permissions(self):
        view = RelatedObjectViewSet()
        view.action = 'create'

        assert [p.__class__ for p in view.get_permissions()] == [IsAuthenticated]
