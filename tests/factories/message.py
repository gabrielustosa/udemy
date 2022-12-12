import factory

from tests.base import AnnotationModelTest
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory

from udemy.apps.message.models import Message


class MessageFactory(AnnotationModelTest):
    class Meta:
        model = Message

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
    content = factory.Faker('sentence')
