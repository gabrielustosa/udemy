from rest_framework import serializers

from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.core.serializers.serializer import ModelSerializer
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
        create_only_fields = ('course',)
        min_fields = ('id', 'rating', 'comment')
        default_fields = (*min_fields, 'creator', 'course')
        permissions_for_field = {
            ('course',): [IsEnrolled]
        }

    def get_likes_count(self, instance):
        return instance.actions.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.actions.filter(action=2).count()

