import factory

from random import randint

from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from udemy.apps.quiz.models import Quiz, Question


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz
        django_get_or_create = ('title', 'description', 'pass_percent', 'module', 'course', 'order')

    title = factory.Faker('name')
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(ModuleFactory)
    description = factory.Faker('sentence')
    pass_percent = 50
    order = None


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question
        django_get_or_create = ('question', 'feedback', 'answers', 'quiz', 'order', 'correct_response', 'course')

    question = factory.Faker('sentence')
    feedback = factory.Faker('sentence')
    answers = factory.List([factory.Faker('sentence') for _ in range(5)])
    quiz = factory.SubFactory(QuizFactory)
    course = factory.SubFactory(CourseFactory)
    correct_response = randint(1, 5)
    order = None
