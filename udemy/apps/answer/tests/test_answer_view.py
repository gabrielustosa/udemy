from tests.base import TestViewBase
from tests.factories.answer import QuestionAnswerFactory, RatingAnswerFactory, MessageAnswerFactory
from tests.factories.message import MessageFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory

from udemy.apps.answer.views import RatingAnswerViewSet, QuestionAnswerViewSet, MessageAnswerViewSet
from udemy.apps.message.models import Message
from udemy.apps.question.models import Question
from udemy.apps.rating.models import Rating


class TestRatingAnswerView(TestViewBase):
    def test_filter_kwargs(self):
        view = self.get_instance(RatingAnswerViewSet, rating_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'rating',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(RatingAnswerViewSet, rating_id=1, action=1, request=self.request)
        view.format_kwarg = None

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Rating)

    def test_queryset_is_correctly_filtering(self):
        rating = RatingFactory()

        view = self.get_instance(RatingAnswerViewSet, rating_id=rating.id, request=self.request)

        QuestionAnswerFactory.create_batch(5)
        ratings = RatingAnswerFactory.create_batch(10, content_object=rating)

        self.assertEqual(list(view.get_queryset()), ratings)


class TestQuestionAnswerView(TestViewBase):
    def test_filter_kwargs(self):
        view = self.get_instance(QuestionAnswerViewSet, question_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'question',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(QuestionAnswerViewSet, question_id=1, action=1, request=self.request)
        view.format_kwarg = None

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Question)

    def test_queryset_is_correctly_filtering(self):
        question = QuestionFactory()

        view = self.get_instance(QuestionAnswerViewSet, question_id=question.id, request=self.request)

        RatingAnswerFactory.create_batch(5)
        questions = QuestionAnswerFactory.create_batch(10, content_object=question)

        self.assertEqual(list(view.get_queryset()), questions)


class TestMessageAnswerView(TestViewBase):
    def test_filter_kwargs(self):
        view = self.get_instance(MessageAnswerViewSet, message_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'message',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(MessageAnswerViewSet, message_id=1, action=1, request=self.request)
        view.format_kwarg = None

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Message)

    def test_queryset_is_correctly_filtering(self):
        message = MessageFactory()

        view = self.get_instance(MessageAnswerViewSet, message_id=message.id, request=self.request)

        RatingAnswerFactory.create_batch(5)
        questions = MessageAnswerFactory.create_batch(10, content_object=message)

        self.assertEqual(list(view.get_queryset()), questions)
