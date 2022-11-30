from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.content import ContentFactory
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory

from udemy.apps.content.models import Content, Link
from udemy.apps.content.serializer import ContentSerializer
from udemy.apps.course.models import CourseRelation

CONTENT_LIST_URL = reverse('content-list')


def content_detail_url(pk): return reverse('content-detail', kwargs={'pk': pk})


class TestContentAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_content(self):
        lesson = LessonFactory()

        lesson.course.instructors.add(self.user)

        payload = {
            'title': 'teste',
            'lesson': lesson.id,
            'course': lesson.course.id,
            'item': {
                'content': 'Teste'
            }
        }
        response = self.client.post(CONTENT_LIST_URL, payload, format='json')

        content = Content.objects.get(id=response.data['id'])

        serializer = ContentSerializer(content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_content_retrieve(self):
        content = ContentFactory()
        CourseRelation.objects.create(creator=self.user, course=content.course)

        response = self.client.get(content_detail_url(content.id))

        serializer = ContentSerializer(content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_partial_content_update(self):
        content = ContentFactory()

        content.course.instructors.add(self.user)

        payload = {
            'item': {
                'url': 'https://google.com'
            }
        }
        response = self.client.patch(content_detail_url(pk=content.id), payload, format='json')

        content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.item.url, payload['item']['url'])
        self.assertTrue(isinstance(content.item, Link))

    def test_content_full_update(self):
        content = ContentFactory()

        content.course.instructors.add(self.user)

        payload = {
            'title': 'teste',
            'item': {
                'url': 'https://google.com'
            }
        }
        response = self.client.put(content_detail_url(pk=content.id), payload, format='json')

        content.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.title, payload['title'])
        self.assertEqual(content.item.url, payload['item']['url'])
        self.assertTrue(isinstance(content.item, Link))

    def test_delete_content(self):
        content = ContentFactory()

        content.course.instructors.add(self.user)

        response = self.client.delete(content_detail_url(pk=content.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Content.objects.filter(id=content.id).exists())
