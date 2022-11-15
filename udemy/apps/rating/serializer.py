from rest_framework import serializers

from udemy.apps.core.fields import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.user.serializer import UserSerializer


class RatingSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = [
            'id', 'course', 'rating', 'comment',
            'creator', 'created', 'modified',
            'likes_count', 'dislikes_count'
        ]
        related_objects = {
            'creator': UserSerializer,
            'course': CourseSerializer
        }

    def get_likes_count(self, instance):
        return instance.actions.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.actions.filter(action=2).count()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
