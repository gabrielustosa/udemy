import factory

from tests.factories.user import UserFactory
from udemy.apps.course.models import Course


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
        django_get_or_create = ('title', 'slug', 'headline', 'is_paid', 'price', 'language')

    title = factory.Faker('name')
    slug = factory.Faker('name')
    headline = factory.Faker('name')
    is_paid = True
    price = 1
    language = 'pt-br'
