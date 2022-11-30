from unittest.mock import patch

from django.http import Http404
from rest_framework.permissions import AllowAny

from tests.base import TestViewBase
from tests.factories.action import QuestionActionFactory, RatingActionFactory, MessageAnswerActionFactory
from tests.factories.answer import MessageAnswerFactory
from tests.factories.question import QuestionFactory
from tests.factories.rating import RatingFactory

from udemy.apps.action.views import RatingActionViewSet, QuestionActionViewSet, AnswerActionViewSet
from udemy.apps.answer.models import Answer
from udemy.apps.question.models import Question
from udemy.apps.rating.models import Rating


class TestRatingView(TestViewBase):

    def test_filter_kwargs(self):
        view = self.get_instance(RatingActionViewSet, rating_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'rating',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_filter_kwargs_with_action(self):
        view = self.get_instance(RatingActionViewSet, rating_id=1, action=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'rating',
            'object_id': 1,
            'action': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(
            RatingActionViewSet,
            rating_id=1,
            action=1,
            request=self.request,
            initkwargs={'format_kwarg': None}
        )

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Rating)

    def test_queryset_is_correctly_filtering(self):
        rating = RatingFactory()

        view = self.get_instance(RatingActionViewSet, rating_id=rating.id, action=1, request=self.request)

        QuestionActionFactory.create_batch(5)
        ratings = RatingActionFactory.create_batch(10, content_object=rating)

        expected_result = filter(lambda r: r.action == 1, ratings)

        self.assertEqual(list(view.get_queryset()), list(expected_result))

    def test_get_object_return_only_action_of_request_user(self):
        rating = RatingFactory(creator=self.user)

        view = self.get_instance(
            RatingActionViewSet,
            rating_id=rating.id,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        QuestionActionFactory.create_batch(5)
        RatingActionFactory.create_batch(10)
        rating_action = RatingActionFactory(content_object=rating, action=1)

        with patch.object(RatingActionViewSet, 'permission_classes_by_action', {('default',): [AllowAny]}):
            self.assertEqual(rating_action, view.get_object())

    def test_get_object_return_404_if_request_user_has_no_action(self):
        view = self.get_instance(
            RatingActionViewSet,
            rating_id=1,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        RatingActionFactory.create_batch(10)
        QuestionActionFactory.create_batch(5)

        with patch.object(RatingActionViewSet, 'permission_classes_by_action', {('default',): [AllowAny]}):
            with self.assertRaises(Http404):
                view.get_object()


class TestQuestionView(TestViewBase):

    def test_filter_kwargs(self):
        view = self.get_instance(QuestionActionViewSet, question_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'question',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_filter_kwargs_with_action(self):
        view = self.get_instance(QuestionActionViewSet, question_id=1, action=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'question',
            'object_id': 1,
            'action': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(
            QuestionActionViewSet,
            question_id=1,
            action=1,
            request=self.request,
            initkwargs={'format_kwarg': None}
        )

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Question)

    def test_queryset_is_correctly_filtering(self):
        question = QuestionFactory()

        view = self.get_instance(QuestionActionViewSet, question_id=question.id, action=1, request=self.request)

        RatingActionFactory.create_batch(5)
        questions = QuestionActionFactory.create_batch(10, content_object=question)

        expected_result = filter(lambda r: r.action == 1, questions)

        self.assertEqual(list(view.get_queryset()), list(expected_result))

    def test_get_object_return_only_action_of_request_user(self):
        question = QuestionFactory(creator=self.user)

        view = self.get_instance(
            QuestionActionViewSet,
            question_id=question.id,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        RatingActionFactory.create_batch(5)
        QuestionActionFactory.create_batch(10)
        question_action = QuestionActionFactory(content_object=question, action=1)

        with patch.object(QuestionActionViewSet, 'permission_classes', []):
            self.assertEqual(question_action, view.get_object())

    def test_get_object_return_404_if_request_user_has_no_action(self):
        view = self.get_instance(
            QuestionActionViewSet,
            question_id=1,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        RatingActionFactory.create_batch(5)
        QuestionActionFactory.create_batch(10)

        with patch.object(QuestionActionViewSet, 'permission_classes', []):
            with self.assertRaises(Http404):
                view.get_object()


class TestAnswerView(TestViewBase):

    def test_filter_kwargs(self):
        view = self.get_instance(AnswerActionViewSet, answer_id=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'answer',
            'object_id': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_filter_kwargs_with_action(self):
        view = self.get_instance(AnswerActionViewSet, answer_id=1, action=1, request=self.request)

        expected_filter_kwargs = {
            'content_type__model': 'answer',
            'object_id': 1,
            'action': 1
        }
        self.assertEqual(view.get_filter_kwargs(), expected_filter_kwargs)

    def test_serializer_context(self):
        view = self.get_instance(
            AnswerActionViewSet,
            answer_id=1,
            action=1,
            request=self.request,
            initkwargs={'format_kwarg': None}
        )

        serializer_context = view.get_serializer_context()

        self.assertEqual(serializer_context['object_id'], 1)
        self.assertEqual(serializer_context['model'], Answer)

    def test_queryset_is_correctly_filtering(self):
        answer = MessageAnswerFactory()

        view = self.get_instance(AnswerActionViewSet, answer_id=answer.id, action=1, request=self.request)

        RatingActionFactory.create_batch(5)
        answers = MessageAnswerActionFactory.create_batch(10, content_object=answer)

        expected_result = filter(lambda r: r.action == 1, answers)

        self.assertEqual(list(view.get_queryset()), list(expected_result))

    def test_get_object_return_only_action_of_request_user_x(self):
        answer = MessageAnswerFactory(creator=self.user)

        view = self.get_instance(
            AnswerActionViewSet,
            answer_id=answer.id,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        RatingActionFactory.create_batch(5)
        MessageAnswerActionFactory.create_batch(10)
        answer_action = MessageAnswerActionFactory(content_object=answer, action=1)

        with patch.object(AnswerActionViewSet, 'permission_classes', []):
            self.assertEqual(answer_action, view.get_object())

    def test_get_object_return_404_if_request_user_has_no_action(self):
        view = self.get_instance(
            AnswerActionViewSet,
            answer_id=1,
            action=1,
            request=self.request,
            initkwargs={'action': 'retrieve'}
        )

        RatingActionFactory.create_batch(5)
        MessageAnswerActionFactory.create_batch(10)

        with patch.object(AnswerActionViewSet, 'permission_classes', []):
            with self.assertRaises(Http404):
                view.get_object()
