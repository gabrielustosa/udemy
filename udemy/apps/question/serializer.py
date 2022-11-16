from rest_framework import serializers

from udemy.apps.core.fields import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.question.models import Question
from udemy.apps.user.serializer import UserSerializer


class QuestionSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'creator', 'lesson', 'title',
            'content', 'created', 'modified',
            'course', 'likes_count', 'dislikes_count'
        ]
        related_objects = {
            'creator': UserSerializer,
            'lesson': LessonSerializer,
            'course': CourseSerializer
        }
        min_fields = ('id', 'title', 'content')
        default_fields = (*min_fields, 'creator', 'course', 'created', 'modified')

    def get_likes_count(self, instance):
        return instance.actions.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.actions.filter(action=2).count()
