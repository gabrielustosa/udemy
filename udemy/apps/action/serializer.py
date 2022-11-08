from rest_framework import serializers

from udemy.apps.action.models import Action
from udemy.apps.answer.models import Answer
from udemy.apps.rating.models import Rating
from udemy.apps.question.models import Question
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.core.fields import GenericRelatedField


class ActionSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = [
            'id',
            'creator',
            'action',
            'course',
            'created',
            'modified',
            'content_object',
        ]

    def create(self, validated_data):
        object_id = self.context['kwargs'].get(self.pk_url_kwarg)
        validated_data['content_object'] = self.model.objects.get(id=object_id)
        return super().create(validated_data)


class RatingActionSerializer(ActionSerializerBase):
    model = Rating
    pk_url_kwarg = 'rating_id'
    content_object = GenericRelatedField(serializer=RatingSerializer())


class QuestionActionSerializer(ActionSerializerBase):
    model = Question
    pk_url_kwarg = 'question_id'
    content_object = GenericRelatedField(serializer=QuestionSerializer())


class AnswerActionSerializer(ActionSerializerBase):
    model = Answer
    pk_url_kwarg = 'answer_id'
    content_object = GenericRelatedField(serializer=AnswerSerializer())
