import factory

from factory import fuzzy

from tests.base import AnnotationModelTest
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory

from udemy.apps.rating.models import Rating


class RatingFactory(AnnotationModelTest):
    class Meta:
        model = Rating

    course = factory.SubFactory(CourseFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    comment = factory.Faker('sentence')
    creator = factory.SubFactory(UserFactory)
