import factory

from factory import fuzzy

from udemy.apps.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Faker('name', locale='pt_br')
    name = factory.Faker('name', locale='pt_br')
    password = fuzzy.FuzzyText(length=24)
    job_title = fuzzy.FuzzyChoice(['Developer', 'Professor'])
    locale = fuzzy.FuzzyChoice(['Brazil', 'Korea'])
    bio = factory.Faker('sentence')
    is_staff = False
