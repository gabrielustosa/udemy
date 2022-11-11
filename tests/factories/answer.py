import factory

from tests.factories.course import CourseFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from udemy.apps.question.models import Answer


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer
        django_get_or_create = ('creator', 'course', 'content')

    creator = factory.SubFactory(UserFactory)
    content_object = factory.SubFactory(QuestionFactory)
    course = factory.SubFactory(CourseFactory)
    content = factory.Faker('sentence')
