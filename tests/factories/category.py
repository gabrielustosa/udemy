import factory

from django.utils.text import slugify

from udemy.apps.category.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Faker('name')

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
