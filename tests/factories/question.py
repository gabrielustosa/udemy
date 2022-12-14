import factory

from tests.base import AnnotationModelTest
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.user import UserFactory

from udemy.apps.question.models import Question


class QuestionFactory(AnnotationModelTest):
    class Meta:
        model = Question

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(LessonFactory, course=factory.SelfAttribute('..course'))
    title = factory.Faker('name')
    content = factory.Faker('sentence')
