import factory

from faker import Faker

from udemy.apps.user.models import User

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'name', 'password', 'username', 'is_staff')

    email = factory.Faker('email')
    username = factory.Faker('name')
    name = factory.Faker('name')
    password = 'admin123'
    is_staff = False
