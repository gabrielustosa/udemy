import factory

from tests.factories.question import QuestionFactory
from tests.factories.user import UserFactory
from udemy.apps.action.models import Action


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action
        django_get_or_create = ('creator', 'action',)

    action = 1
    creator = factory.SubFactory(UserFactory)
    content_object = factory.SubFactory(QuestionFactory)

