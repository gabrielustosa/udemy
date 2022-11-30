from django.test import TestCase

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.category import CategoryFactory
from tests.factories.user import UserFactory
from udemy.apps.category.models import Category
from udemy.apps.category.serializer import CategorySerializer

CATEGORY_LIST_URL = reverse('category-list')


def category_detail_url(pk): return reverse('category-detail', kwargs={'pk': pk})


class TestCategoryUnauthenticatedRequests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_category_list(self):
        categories = CategoryFactory.create_batch(5)

        response = self.client.get(CATEGORY_LIST_URL)

        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_retrieve(self):
        category = CategoryFactory()

        response = self.client.get(category_detail_url(category.id))

        serializer = CategorySerializer(category)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class TestCategoryAuthenticatedRequests(TestCase):
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

        category = Category.objects.get(id=response.data['id'])

        serializer = CategorySerializer(category)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

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

    def test_full_category_update(self):
        category = CategoryFactory()

        payload = {
            'title': 'string',
            'slug': 'slug',
        }
        response = self.client.put(category_detail_url(pk=category.id), payload)

        category.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(category.title, payload['title'])
        self.assertEqual(category.slug, payload['slug'])

    def test_delete_category(self):
        category = CategoryFactory()

        response = self.client.delete(category_detail_url(pk=category.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
