from rest_framework import serializers

from udemy.apps.action.models import Action
from udemy.apps.core.fields import ActionGenericField
from udemy.apps.question.models import Question, Answer
from udemy.apps.rating.models import Rating


class ActionSerializer(serializers.ModelSerializer):
    content_object = ActionGenericField([Question, Rating, Answer])

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
        extra_kwargs = {'creator': {'read_only': True}}
