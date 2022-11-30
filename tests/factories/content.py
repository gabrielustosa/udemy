import factory

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory

from udemy.apps.content import models


class TextFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Text

    content = factory.Faker('sentence')


class LinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Link

    url = 'https://google.com'


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Image

    image = factory.django.ImageField()


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.File

    file = factory.django.FileField()


class ContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Content

    title = factory.Faker('name')
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(LessonFactory, course=factory.SelfAttribute('..course'))
    item = factory.SubFactory(TextFactory)
