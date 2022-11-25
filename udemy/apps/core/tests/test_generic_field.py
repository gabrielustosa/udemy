from django.test import TestCase

from rest_framework.serializers import ListSerializer

from udemy.apps.content.models import Text, Link
from udemy.apps.content.serializer import TextSerializer, LinkSerializer
from udemy.apps.core.fields import GenericField


class GenericFieldTests(TestCase):
    def setUp(self):
        self.text = Text.objects.create(content='Test content')
        self.link = Link.objects.create(url='https://google.com')
        self.link2 = Link.objects.create(url='https://youtube.com')

        self.serializer = GenericField({
            Text: TextSerializer(),
            Link: LinkSerializer()
        })

        self.list_serializer = ListSerializer(child=self.serializer)

    def test_serialize(self):
        self.assertEqual(
            self.serializer.to_representation(self.text),
            {'content': 'Test content'},
        )
        self.assertEqual(
            self.serializer.to_representation(self.link),
            {'url': 'https://google.com'},
        )

    def test_deserializer(self):
        text = self.serializer.to_internal_value({'content': 'Test content'})
        link = self.serializer.to_internal_value({'url': 'https://google.com'})
        self.assertTrue(isinstance(text, Text))
        self.assertTrue(isinstance(link, Link))

    def test_serialize_list(self):
        actual = self.list_serializer.to_representation([
            self.text, self.link, self.link2, self.text,
        ])
        expected = [
            {'content': 'Test content'},
            {'url': 'https://google.com'},
            {'url': 'https://youtube.com'},
            {'content': 'Test content'},
        ]
        self.assertEqual(actual, expected)

    def test_deserializer_list(self):
        validated_data = self.list_serializer.to_internal_value([
            {'content': 'Test content'},
            {'url': 'https://google.com'},
            {'url': 'https://youtube.com'},
            {'content': 'Test content'},
        ])

        instances = [Text, Link, Link, Text]

        for index, instance in enumerate(instances):
            self.assertTrue(isinstance(validated_data[index], instance))
