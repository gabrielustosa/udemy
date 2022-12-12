from udemy.apps.answer.models import Answer
from udemy.apps.core.fields import GenericRelatedField
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.message.models import Message
from udemy.apps.message.serializer import MessageSerializer
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.user.serializer import UserSerializer


class AnswerSerializer(ModelSerializer):
    content_object = GenericRelatedField({
        Rating: RatingSerializer(),
        Question: QuestionSerializer(),
        Message: MessageSerializer(),
    }, read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'creator', 'content',
            'created', 'modified', 'course',
            'content_object',
        ]
        related_objects = {
            'creator': {
                'serializer': UserSerializer
            },
            'course': {
                'serializer': CourseSerializer
            }
        }
        create_only_fields = ('course',)
        min_fields = ('id', 'content')
        default_fields = (*min_fields, 'creator', 'content_object')
        permissions_for_field = {
            ('course',): [IsEnrolled]
        }


    def create(self, validated_data):
        Model = self.context.get('model')
        object_id = self.context.get('object_id')
        validated_data['content_object'] = Model.objects.get(id=object_id)
        return super().create(validated_data)
