from unittest.mock import patch

from parameterized import parameterized

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from tests.factories.course import CourseFactory
from tests.factories.message import MessageFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory

from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.message.models import Message
from udemy.apps.question.models import Question
from udemy.apps.rating.models import Rating


class TestAnswerSerializer(TestCase):
    @parameterized.expand([
        (RatingFactory, Rating),
        (MessageFactory, Message),
        (QuestionFactory, Question)
    ])
    def test_answer_content_object_is_generated(self, Factory, model):
        with patch.object(AnswerSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()

            data = {
                'content': 'Content.',
                'course': course.id,
            }

            obj = Factory()
            serializer = AnswerSerializer(data=data, context={'model': model, 'object_id': obj.id})
            serializer.is_valid()
            validated_data = serializer.validated_data
            validated_data['creator'] = obj.creator

            answer = serializer.create(validated_data)

            self.assertEqual(answer.content_object, obj)

    def test_invalid_object_id(self):
        with patch.object(AnswerSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()
            data = {
                'content': 'Content.',
                'course': course.id,
            }

            with self.assertRaises(ObjectDoesNotExist):
                serializer = AnswerSerializer(data=data, context={'model': Rating, 'object_id': 321})
                serializer.is_valid()
                serializer.save()

    def test_missing_object_id(self):
        with patch.object(AnswerSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()
            data = {
                'content': 'Content.',
                'course': course.id,
            }

            with self.assertRaises(ObjectDoesNotExist):
                serializer = AnswerSerializer(data=data, context={'model': Rating})
                serializer.is_valid()
                serializer.save()
