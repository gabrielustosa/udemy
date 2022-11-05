from rest_framework import serializers

from udemy.apps.question.models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'creator', 'lesson', 'title',
            'content', 'created', 'modified',
            'course', 'likes_count', 'dislikes_count'
        ]

    def get_likes_count(self, instance):
        return instance.action.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.action.filter(action=2).count()

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be greater than 5 characters')
        return value

    def validate_content(self, value):
        if len(value) > 999:
            raise serializers.ValidationError('Content must be less than 999 characters')
        return value


class AnswerSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'id', 'creator', 'question', 'content',
            'created', 'modified', 'course',
            'likes_count', 'dislikes_count'
        ]

    def get_likes_count(self, instance):
        return instance.action.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.action.filter(action=2).count()

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be greater than 5 characters')
        return value

    def validate_content(self, value):
        if len(value) > 999:
            raise serializers.ValidationError('Content must be less than 999 characters')
        return value
