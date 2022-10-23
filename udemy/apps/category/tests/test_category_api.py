from django.test import TestCase

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.utils import create_factory_in_batch
from tests.factories.category import CategoryFactory
from tests.factories.user import UserFactory
from udemy.apps.category.models import Category
from udemy.apps.category.serializer import CategorySerializer

CATEGORY_LIST_URL = reverse('category-list')


def category_detail_url(pk): return reverse('category-detail', kwargs={'pk': pk})


class PublicCategoryAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_category_list(self):
        categories = create_factory_in_batch(CategoryFactory, 5)

        response = self.client.get(CATEGORY_LIST_URL)

        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_retrieve(self):
        category = CategoryFactory()

        response = self.client.get(category_detail_url(pk=1))

        serializer = CategorySerializer(category)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_category(self):
        response = self.client.post(CATEGORY_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_cant_create_category(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(CATEGORY_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCategoryApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_create_category(self):
        payload = {
            'title': 'string',
            'slug': 'slug',
        }
        response = self.client.post(CATEGORY_LIST_URL, payload)

        category = Category.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], category.title)

    def test_partial_category_update(self):
        original_slug = 'original_slug'
        category = CategoryFactory(slug=original_slug)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(category_detail_url(pk=category.id), payload)

        category.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(category.title, payload['title'])
        self.assertEqual(category.slug, original_slug)

    def test_category_full_update(self):
        category = CategoryFactory()

        payload = {
            'title': 'string',
            'slug': 'slug',
        }
        response = self.client.put(category_detail_url(pk=category.id), payload)

        category.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(category, k), v)

    def test_delete_category(self):
        category = CategoryFactory()

        response = self.client.delete(category_detail_url(pk=category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
