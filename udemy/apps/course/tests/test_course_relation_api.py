from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.user import UserFactory

COURSE_RELATION_LIST_URL = reverse('course_relation-list')


def course_relation_detail_url(pk): return reverse('course_relation-detail', kwargs={'pk': pk})


class PublicCourseRelationAPITest(TestCase):
    """Test unauthenticated API requests."""

    def test_unauthenticated_cant_create_course_relation(self):
        response = self.client.post(COURSE_RELATION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCourseRelationAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
