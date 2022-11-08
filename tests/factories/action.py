import factory

from tests.factories.course import CourseFactory
from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action
        django_get_or_create = ('creator', 'action', 'course')

    action = 1
    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    content_object = factory.SubFactory(QuestionFactory)
