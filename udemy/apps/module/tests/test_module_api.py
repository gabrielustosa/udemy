from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.utils import create_factory_in_batch
from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation

from udemy.apps.module.models import Module
from udemy.apps.module.serializer import ModuleSerializer

MODULE_LIST_URL = reverse('module-list')


def module_detail_url(pk): return reverse('module-detail', kwargs={'pk': pk})


class PublicModuleAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_module(self):
        response = self.client.post(MODULE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateModuleApiTests(TestCase):
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

        module = Module.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(module.title, payload['title'])

    def test_module_retrieve(self):
        module = ModuleFactory()
        CourseRelation.objects.create(creator=self.user, course=module.course)

        response = self.client.get(module_detail_url(module.id))

        serializer = ModuleSerializer(module)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_not_enrolled_can_retrieve_module(self):
        module = ModuleFactory()

        response = self.client.get(module_detail_url(module.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_module_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(module_detail_url(pk=module.id), payload)

        module.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(module.title, payload['title'])

    def test_module_full_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)

        payload = {
            'title': 'string',
            'order': 1,
        }
        response = self.client.put(module_detail_url(pk=module.id), payload)

        module.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_course(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)

        response = self.client.delete(module_detail_url(pk=module.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Module.objects.filter(id=module.id).exists())

    def test_not_course_instructor_cant_create_a_module(self):
        course = CourseFactory()

        payload = {
            'title': 'string',
            'course': course.id
        }
        response = self.client.post(MODULE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_update_module(self):
        module = ModuleFactory()

        user = UserFactory()
        self.client.force_authenticate(user)

        response_patch = self.client.patch(module_detail_url(pk=module.id))
        response_put = self.client.put(module_detail_url(pk=module.id))

        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_module(self):
        module = ModuleFactory()

        response = self.client.delete(module_detail_url(pk=module.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        (3, 6),
        (8, 2),
        (1, 10),
        (9, 2),
        (10, 2),
        (5, 5),
    ])
    def test_module_reorder_field(self, current_order, new_order):
        course = CourseFactory()
        course.instructors.add(self.user)

        create_factory_in_batch(ModuleFactory, 10, course=course)

        module = Module.objects.filter(order=current_order).first()

        payload = {
            'order': new_order
        }

        response = self.client.patch(module_detail_url(pk=module.id), payload)

        module.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(module.order, new_order)

        for index, model in enumerate(Module.objects.all(), start=1):
            self.assertEqual(model.order, index)

    def test_module_order_is_generated_correctly(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        create_factory_in_batch(ModuleFactory, 10, course=course)

        for index, model in enumerate(Module.objects.all(), start=1):
            self.assertEqual(model.order, index)
