from rest_framework import serializers

from udemy.apps.action.models import Action
from udemy.apps.core.fields import ActionGenericField
from udemy.apps.question.models import Question, Answer
from udemy.apps.question.serializer import QuestionSerializer, AnswerSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer


class ActionSerializer(serializers.ModelSerializer):
    content_object = ActionGenericField({
        Question: QuestionSerializer(),
        Answer: AnswerSerializer(),
        Rating: RatingSerializer(),
    })

    class Meta:
        model = Action
        fields = [
            'id',
            'creator',
            'action',
            'created',
            'modified',
            'content_object',
        ]
