import factory

from django.contrib.contenttypes.models import ContentType

from tests.factories.course import CourseFactory
from tests.factories.message import MessageFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory

from udemy.apps.question.models import Answer


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        exclude = ['content_object']
        abstract = True

    creator = factory.SelfAttribute('content_object.creator')
    course = factory.SelfAttribute('content_object.course')
    content = factory.Faker('sentence')
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(o.content_object))


class RatingAnswerFactory(AnswerFactory):
    content_object = factory.SubFactory(RatingFactory)

    class Meta:
        model = Answer


class QuestionAnswerFactory(AnswerFactory):
    content_object = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Answer


class MessageAnswerFactory(AnswerFactory):
    content_object = factory.SubFactory(MessageFactory)

    class Meta:
        model = Answer
