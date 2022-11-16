from udemy.apps.action.models import Action
from udemy.apps.answer.models import Answer
from udemy.apps.answer.serializer import AnswerSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.core.fields import GenericField, ModelSerializer
from udemy.apps.user.serializer import UserSerializer


class ActionSerializer(ModelSerializer):
    content_object = GenericField({
        Rating: RatingSerializer(),
        Answer: AnswerSerializer(),
        Question: QuestionSerializer()
    }, required=False)

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
        related_objects = {
            'creator': UserSerializer,
            'course': CourseSerializer
        }
        min_fields = ('id', 'action')
        default_fields = (*min_fields, 'creator', 'course', 'content_object')

    def create(self, validated_data):
        Model = self.context.get('model')
        object_id = self.context.get('object_id')
        validated_data['content_object'] = Model.objects.get(id=object_id)
        return super().create(validated_data)
