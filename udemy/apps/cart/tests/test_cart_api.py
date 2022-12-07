from decimal import Decimal

from django.test import TestCase
from rest_framework.reverse import reverse

from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer

CART_LIST = reverse('cart:list')


def cart_detail(pk):
    return reverse('cart:detail', kwargs={'course_id': pk})


class TestCartAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_cart_add(self):
        course = CourseFactory()

        self.client.post(cart_detail(course.id))

        assert self.client.session['cart'] == [course.id]

    def test_cart_remove(self):
        course = CourseFactory()

        self.client.delete(cart_detail(course.id))

        assert self.client.session['cart'] == []

    def test_cart_list(self):
        course = CourseFactory()

        self.client.post(cart_detail(course.id))

        response = self.client.get(CART_LIST)

        expected_data = [
            CourseSerializer(course, fields=(
            'id', 'title', 'url', 'is_paid', 'price', 'instructors', 'num_subscribers', 'avg_rating', 'created')).data
        ]

        assert response.data == expected_data
