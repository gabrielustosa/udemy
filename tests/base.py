import base64
import factory

from test_plus.test import CBVTestCase

from rest_framework.test import APIRequestFactory
from rest_framework import HTTP_HEADER_ENCODING

from tests.factories.user import UserFactory

request_factory = APIRequestFactory()


def basic_auth_header(username, password):
    credentials = ('%s:%s' % (username, password))
    base64_credentials = base64.b64encode(credentials.encode(HTTP_HEADER_ENCODING)).decode(HTTP_HEADER_ENCODING)
    return 'Basic %s' % base64_credentials


class TestViewBase(CBVTestCase):
    permitted_credentials = basic_auth_header('permitted', 'password')

    def setUp(self):
        self.user = UserFactory()
        self.request = request_factory.get(
            '/',
            format='json',
            HTTP_AUTHORIZATION=self.permitted_credentials,
        )
        self.request.user = self.user
        self.request.data = dict()
        self.request.query_params = {}


class AnnotationModelTest(factory.django.DjangoModelFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = super()._create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.get(id=obj.id)
