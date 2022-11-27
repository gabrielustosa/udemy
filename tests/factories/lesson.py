import factory

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from udemy.apps.lesson.models import Lesson


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson
        django_get_or_create = ('title', 'video', 'video_id', 'video_duration', 'module', 'course', 'order')

    title = factory.Faker('name')
    video = 'https://www.youtube.com/watch?v=Ejkb_YpuHWs&list=PLHz_AreHm4dkZ9-atkcmcBaMZdmLHft8n&ab_channel=CursoemV%C3%ADdeo'
    video_id = 'E6CdIawPTh0'
    video_duration = 1
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(ModuleFactory, course=factory.SelfAttribute('..course'))
    order = None
