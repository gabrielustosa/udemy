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

    def get_likes_count(self, instance):
        return instance.actions.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.actions.filter(action=2).count()

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be greater than 5 characters')
        return value

    def validate_content(self, value):
        if len(value) > 999:
            raise serializers.ValidationError('Content must be less than 999 characters')
        return value
