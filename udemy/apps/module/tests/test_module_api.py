from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation

from udemy.apps.module.models import Module
from udemy.apps.module.serializer import ModuleSerializer

MODULE_LIST_URL = reverse('module-list')


def module_detail_url(pk): return reverse('module-detail', kwargs={'pk': pk})


class TestModuleUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_module(self):
        response = self.client.post(MODULE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestModuleAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_module(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        payload = {
            'title': 'string',
            'course': course.id
        }
        response = self.client.post(MODULE_LIST_URL, payload)

        module = Module.objects.get(id=response.data['id'])

        serializer = ModuleSerializer(module)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_module_retrieve(self):
        module = ModuleFactory()
        CourseRelation.objects.create(creator=self.user, course=module.course)

        response = self.client.get(module_detail_url(module.id))

        serializer = ModuleSerializer(module)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_module_update(self):
        module = ModuleFactory()

        module.course.instructors.add(self.user)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(module_detail_url(pk=module.id), payload)

        module.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(module.title, payload['title'])

    def test_module_full_update(self):
        module = ModuleFactory()

        module.course.instructors.add(self.user)

        payload = {
            'title': 'string',
            'order': 1,
        }
        response = self.client.put(module_detail_url(pk=module.id), payload)

        module.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_module(self):
        module = ModuleFactory()

        module.course.instructors.add(self.user)

        response = self.client.delete(module_detail_url(pk=module.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Module.objects.filter(id=module.id).exists())
