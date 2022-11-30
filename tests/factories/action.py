import factory

from factory import fuzzy

from django.contrib.contenttypes.models import ContentType

from tests.factories.answer import RatingAnswerFactory, QuestionAnswerFactory, MessageAnswerFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory

from udemy.apps.action.models import Action


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        exclude = ['content_object']
        abstract = True

    action = fuzzy.FuzzyChoice([1, 2])
    creator = factory.SelfAttribute('content_object.creator')
    course = factory.SelfAttribute('content_object.course')
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(o.content_object))

    @classmethod
    def create_batch(cls, size, **kwargs):
        return [cls.create(**kwargs, creator=UserFactory()) for _ in range(size)]


class QuestionActionFactory(ActionFactory):
    content_object = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Action


class RatingActionFactory(ActionFactory):
    content_object = factory.SubFactory(RatingFactory)

    class Meta:
        model = Action


class RatingAnswerActionFactory(ActionFactory):
    content_object = factory.SubFactory(RatingAnswerFactory)

    class Meta:
        model = Action


class QuestionAnswerActionFactory(ActionFactory):
    content_object = factory.SubFactory(QuestionAnswerFactory)

    class Meta:
        model = Action


class MessageAnswerActionFactory(ActionFactory):
    content_object = factory.SubFactory(MessageAnswerFactory)

    class Meta:
        model = Action
