import factory

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from udemy.apps.content.models import Content, Text


class ContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Content
        django_get_or_create = ('title', 'lesson', 'course', 'order')

    title = factory.Faker('name')
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(LessonFactory, course=factory.SelfAttribute('..course'))
    order = None
    item = (Text, {'content': 'Test content'})

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        Model, value = kwargs.pop('item')
        item = Model.objects.create(**value)
        kwargs['item'] = item
        return super()._create(model_class, *args, **kwargs)
