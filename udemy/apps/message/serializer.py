from udemy.apps.core.fields import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.message.models import Message
from udemy.apps.user.serializer import UserSerializer


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'creator', 'title',
            'content', 'created', 'modified',
            'course'
        ]
        related_objects = {
            'creator': UserSerializer,
            'course': CourseSerializer
        }
        min_fields = ('id', 'title', 'content')
        default_fields = (*min_fields, 'creator', 'course')
