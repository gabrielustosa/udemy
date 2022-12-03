from django.core.exceptions import ValidationError
from django.test import TestCase

from parameterized import parameterized

from udemy.apps.core.models import ModelTest, ModelRelatedObject


class TestOrderedModel(TestCase):
    def test_get_queryset_in_respect_to(self):
        model_test = ModelTest.objects.create(title='test 1')
        model_test_2 = ModelTest.objects.create(title='test 2')
        ModelRelatedObject.objects.create(title='1', model_test=model_test_2)
        related_object = ModelRelatedObject.objects.create(title='1', model_test=model_test)

        assert list(related_object.get_queryset()) == [related_object]

    def test_get_last_order(self):
        model_test = ModelTest.objects.create(title='test 1')
        ModelRelatedObject.objects.create(title='1', model_test=model_test)
        ModelRelatedObject.objects.create(title='1', model_test=model_test)
        related_object = ModelRelatedObject.objects.create(title='1', model_test=model_test)

        assert related_object.get_last_order() == 3

    def test_get_next_order(self):
        model_test = ModelTest.objects.create(title='test 1')
        ModelRelatedObject.objects.create(title='1', model_test=model_test)
        ModelRelatedObject.objects.create(title='1', model_test=model_test)
        related_object = ModelRelatedObject.objects.create(title='1', model_test=model_test)

        assert related_object.get_next_order() == 4

    def test_do_after_create(self):
        model_test = ModelTest.objects.create(title='test 1')
        ModelRelatedObject.objects.create(title='1', model_test=model_test)

        assert ModelTest.objects.filter(title='create', num=99).exists()

    def test_do_after_update(self):
        model_test = ModelTest.objects.create(title='test 1')
        related_object = ModelRelatedObject.objects.create(title='1', model_test=model_test)
        related_object.order = 1
        related_object.save()

        assert ModelTest.objects.filter(title='update', num=100).exists()

    def test_cant_save_order_greater_than_last_order(self):
        model_test = ModelTest.objects.create(title='test 1')
        related_object = ModelRelatedObject.objects.create(title='1', model_test=model_test)

        with self.assertRaises(ValidationError):
            related_object.order = 2
            related_object.save()

    def test_order_generation(self):
        model_test = ModelTest.objects.create(title='test 1')
        create_model_in_batch(5, title='title', model_test=model_test)

        model_test_2 = ModelTest.objects.create(title='test 2')
        create_model_in_batch(5, title='title', model_test=model_test_2)

        for index, model in enumerate(ModelRelatedObject.objects.filter(model_test=model_test), start=1):
            assert model.order == index

    def test_order_update(self):
        model_test = ModelTest.objects.create(title='test 1')
        create_model_in_batch(10, title='title', model_test=model_test)

        model = ModelRelatedObject.objects.filter(order=5).first()

        model.order = 10
        model.save()

        assert model.order == 10

    @parameterized.expand([
        (3, 6),
        (8, 2),
        (1, 10),
        (9, 2),
        (10, 2),
        (5, 5),
    ])
    def test_order_update_model_all_orders(self, current_order, new_order):
        model_test = ModelTest.objects.create(title='test 1')
        create_model_in_batch(10, title='title', model_test=model_test)

        model = ModelRelatedObject.objects.filter(order=current_order).first()

        model.order = new_order
        model.save()

        for index, model in enumerate(ModelRelatedObject.objects.filter(model_test=model_test), start=1):
            assert model.order == index

    def test_delete_ordered_model(self):
        model_test = ModelTest.objects.create(title='test 1')
        create_model_in_batch(10, title='title', model_test=model_test)

        model = ModelRelatedObject.objects.filter(order=5).first()

        model.delete()

        for index, model in enumerate(ModelRelatedObject.objects.filter(model_test=model_test), start=1):
            assert model.order == index


def create_model_in_batch(batch, **kwargs):
    return [ModelRelatedObject.objects.create(**kwargs) for _ in range(batch)]
