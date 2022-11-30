import factory

from factory import fuzzy

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory

from udemy.apps.lesson.models import Lesson


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    title = factory.Faker('name')
    video_id = fuzzy.FuzzyText()
    video = factory.LazyAttributeSequence(lambda l, n: 'https://www.youtube.com/watch?v=%s' % l.video_id)
    video_duration = fuzzy.FuzzyInteger(60)
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(ModuleFactory, course=factory.SelfAttribute('..course'))
