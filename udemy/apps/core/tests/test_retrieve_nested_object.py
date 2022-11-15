from django.test import TestCase
from rest_framework.reverse import reverse

from rest_framework.test import APIClient

from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory


class RetrieveNestedObjectTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_nested_objects_retrieve(self):
        module = ModuleFactory()
        url = reverse('module-detail', kwargs={'pk': 1})

        response = self.client.get(f'{url}?field[course]=title,is_paid,slug')

        expected_response = {
            'id': module.id,
            'title': module.title,
            'order': module.order,
            'course': {
                'title': module.course.title,
                'is_paid': module.course.is_paid,
                'slug': module.course.slug
            }
        }

        self.assertEqual(response.data, expected_response)
