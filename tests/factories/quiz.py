import factory

from factory import fuzzy

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory

from udemy.apps.quiz.models import Quiz, Question


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    title = factory.Faker('name')
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(ModuleFactory, course=factory.SelfAttribute('..course'))
    description = factory.Faker('sentence')
    is_published = factory.Faker('boolean')
    pass_percent = fuzzy.FuzzyInteger(1, 100)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    question = factory.Faker('sentence')
    feedback = factory.Faker('sentence')
    answers = factory.List([factory.Faker('sentence') for _ in range(5)])
    course = factory.SubFactory(CourseFactory)
    quiz = factory.SubFactory(QuizFactory, course=factory.SelfAttribute('..course'))
    correct_response = fuzzy.FuzzyInteger(1, 5)
