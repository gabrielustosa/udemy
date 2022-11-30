from unittest.mock import patch

from parameterized import parameterized

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from tests.factories.answer import MessageAnswerFactory
from tests.factories.course import CourseFactory
from tests.factories.quiz import QuestionFactory
from tests.factories.rating import RatingFactory

from udemy.apps.action.serializer import ActionSerializer
from udemy.apps.answer.models import Answer
from udemy.apps.quiz.models import Question
from udemy.apps.rating.models import Rating


class TestActionSerializer(TestCase):
    @parameterized.expand([
        (RatingFactory, Rating),
        (QuestionFactory, Question),
        (MessageAnswerFactory, Answer),
    ])
    def test_action_content_object_is_generated(self, Factory, model):
        with patch.object(ActionSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()
            data = {
                'action': 1,
                'course': course.id,
            }
            obj = Factory()

            serializer = ActionSerializer(data=data, context={'model': model, 'object_id': obj.id})
            serializer.is_valid()
            action = serializer.save()

            self.assertEqual(action.content_object, obj)

    def test_invalid_object_id(self):
        with patch.object(ActionSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()
            data = {
                'action': 1,
                'course': course.id,
            }

            with self.assertRaises(ObjectDoesNotExist):
                serializer = ActionSerializer(data=data, context={'model': Rating, 'object_id': 321})
                serializer.is_valid()
                serializer.save()

    def test_missing_object_id(self):
        with patch.object(ActionSerializer.Meta, 'permissions_for_field', {}):
            course = CourseFactory()
            data = {
                'action': 1,
                'course': course.id,
            }

            with self.assertRaises(ObjectDoesNotExist):
                serializer = ActionSerializer(data=data, context={'model': Rating})
                serializer.is_valid()
                serializer.save()
