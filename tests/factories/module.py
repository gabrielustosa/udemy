import factory

from tests.factories.course import CourseFactory

from udemy.apps.module.models import Module


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
