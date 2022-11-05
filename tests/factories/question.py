import factory

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory
from udemy.apps.question.models import Question


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question
        django_get_or_create = ('creator', 'lesson', 'title', 'content', 'course')

    creator = factory.SubFactory(UserFactory)
    lesson = factory.SubFactory(LessonFactory)
    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
    content = factory.Faker('sentence')
