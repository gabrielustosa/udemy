from django.test import TestCase

from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class TestUpdateCreateOnlyFields(TestCase):
    def test_create_only_fields(self):
        class CreateOnlySerializer(ModelSerializer):
            class Meta:
                model = ModelTest
                fields = ('id', 'title', 'num')
                create_only_fields = ('num',)

        data = {'title': 'new title', 'num': 8}
        model_test = ModelTest.objects.create(title='test')
        serializer = CreateOnlySerializer(instance=model_test, data=data)
        serializer.is_valid()
        model_test = serializer.save()

        assert model_test.title == data['title']
        assert model_test.num == 0

    def test_update_only_fields(self):
        class UpdateOnlySerializer(ModelSerializer):
            class Meta:
                model = ModelTest
                fields = ('id', 'title', 'num')
                update_only_fields = ('num',)

        data = {'title': 'new title', 'num': 7}
        serializer = UpdateOnlySerializer(data=data)
        serializer.is_valid()
        model_test = serializer.save()

        assert model_test.title == data['title']
        assert model_test.num == 0
