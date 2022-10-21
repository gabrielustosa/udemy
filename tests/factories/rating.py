import factory

from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory
from udemy.apps.rating.models import Rating


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating
        django_get_or_create = ('course', 'rating', 'comment', 'creator')

    course = factory.SubFactory(CourseFactory)
    rating = 4
    comment = factory.Faker('sentence')
    creator = factory.SubFactory(UserFactory)
