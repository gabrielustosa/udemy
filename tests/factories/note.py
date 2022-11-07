import factory

from django.utils import timezone

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory
from udemy.apps.note.models import Note


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note
        django_get_or_create = ('creator', 'lesson', 'course', 'note', 'time')

    creator = factory.SubFactory(UserFactory)
    lesson = factory.SubFactory(LessonFactory)
    course = factory.SubFactory(CourseFactory)
    note = factory.Faker('sentence')
    time = factory.Faker('date_time', tzinfo=timezone.get_current_timezone())
