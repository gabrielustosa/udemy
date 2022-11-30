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
    is_paid = factory.Faker('boolean')
    price = fuzzy.FuzzyInteger(150)
    language = fuzzy.FuzzyChoice(['pt-br', 'en', 'es'])
    requirements = factory.Faker('sentence')
    what_you_will_learn = factory.Faker('sentence')
    level = fuzzy.FuzzyChoice(['beginner', 'intermediary', 'advanced'])

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
