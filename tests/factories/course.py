import factory

from factory import fuzzy

from django.utils.text import slugify

from udemy.apps.course.models import Course


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker('name')
    headline = factory.Faker('sentence')
    description = factory.Faker('sentence')
    price = fuzzy.FuzzyFloat(0, 1)
    language = fuzzy.FuzzyChoice(['pt-br', 'en', 'es'])
    requirements = factory.Faker('sentence')
    what_you_will_learn = factory.Faker('sentence')
    level = fuzzy.FuzzyChoice(['beginner', 'intermediary', 'advanced'])

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)

    @factory.lazy_attribute
    def is_paid(self):
        return self.price == 0
