import factory

from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory

from udemy.apps.message.models import Message


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message
        django_get_or_create = ('creator', 'course', 'title', 'content')

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
    content = factory.Faker('sentence')
