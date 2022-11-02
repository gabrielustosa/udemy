from rest_framework import serializers

from udemy.apps.question.models import Question, Answer
from udemy.apps.user.models import User


class QuestionSerializer(serializers.ModelSerializer):
    liked_by = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Question
        fields = [
            'id', 'creator', 'lesson', 'title',
            'content', 'liked_by', 'created',
            'modified'
        ]

    def validate(self, attrs):
        if len(attrs['title']) < 5:
            raise serializers.ValidationError('Title must be greater than 5 characters')
        if len(attrs['content']) > 999:
            raise serializers.ValidationError('Content must be less than 5 characters')
        return attrs

    def update(self, instance, validated_data):
        liked_by = validated_data.pop('liked_by')
        for i in liked_by:
            instance.liked_by.add(i)
        instance.save()
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    liked_by = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Answer
        fields = [
            'id', 'creator', 'question', 'content',
            'liked_by', 'created', 'modified'
        ]

    def validate(self, attrs):
        if len(attrs['title']) < 5:
            raise serializers.ValidationError('Title must greater than 5 characters')
        if len(attrs['content']) > 999:
            raise serializers.ValidationError('Content must have less than 5 characters')
        return attrs

    def update(self, instance, validated_data):
        liked_by = validated_data.pop('liked_by')
        for i in liked_by:
            instance.liked_by.add(i)
        instance.save()
        return instance
