from django.test import TestCase

from udemy.apps.core.models import ModelTest
from udemy.apps.core.serializer import ModelSerializer


class CreateOnlySerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'num')
        create_only_fields = ('num',)


class UpdateOnlySerializer(ModelSerializer):
    class Meta:
        model = ModelTest
        fields = ('id', 'title', 'num')
        update_only_fields = ('num',)


class TestCreateOnlyFields(TestCase):

    def test_create_only_fields(self):
        data = {'title': 'new title', 'num': 8}
        model_test = ModelTest.objects.create(title='test')
        serializer = CreateOnlySerializer(instance=model_test, data=data)
        serializer.is_valid()
        model_test = serializer.save()

        assert model_test.title == data['title']
        assert model_test.num == 0

    def test_create_only_fields_internal_value(self):
        data = {'title': 'new title', 'num': 8}
        model_test = ModelTest.objects.create(title='test')

        ret = CreateOnlySerializer(instance=model_test).to_internal_value(data)

        assert ret == {'title': 'new title'}

    def test_create_only_fields_are_setting_to_required_false(self):
        model_test = ModelTest.objects.create(title='test')

        extra_kwargs = CreateOnlySerializer(instance=model_test).get_extra_kwargs()

        assert extra_kwargs == {'num': {'required': False}}


class TestUpdateOnlyFields(TestCase):
    def test_update_only_fields(self):
        data = {'title': 'new title', 'num': 7}
        serializer = UpdateOnlySerializer(data=data)
        serializer.is_valid()
        model_test = serializer.save()

        assert model_test.title == data['title']
        assert model_test.num == 0

    def test_update_only_fields_internal_value(self):
        data = {'title': 'new title', 'num': 8}

        ret = UpdateOnlySerializer().to_internal_value(data)

        assert ret == {'title': 'new title'}
