import factory

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory

from udemy.apps.note.models import Note


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(LessonFactory, course=factory.SelfAttribute('..course'))
    note = factory.Faker('sentence')
    time = factory.Faker('time')
