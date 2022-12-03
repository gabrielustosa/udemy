from django.test import TestCase, RequestFactory

from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins.view import RetrieveRelatedObjectMixin
from udemy.apps.core.models import ModelRelatedObject


class RelatedObjectViewSet(RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = ModelRelatedObject.objects.all()

    class Meta:
        model = ModelRelatedObject


factory = RequestFactory()
request = factory.get('/')


class TestRetrieveRelatedObjectView(TestCase):
    def test_related_fields_retrieve(self):
        view = RelatedObjectViewSet(request=request)
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        assert view.related_fields == {'model_test': ['id', 'name']}

    def test_fields_in_serializer_context(self):
        view = RelatedObjectViewSet(request=request)
        view.format_kwarg = None
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        assert view.get_serializer_context()['fields'] == {'model_test': ['id', 'name']}

    def test_optimize_queryset(self):
        view = RelatedObjectViewSet(request=request)
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        with self.assertNumQueries(1):
            list(view.get_queryset())
