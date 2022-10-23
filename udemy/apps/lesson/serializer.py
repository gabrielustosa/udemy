from rest_framework import serializers

from udemy.apps.lesson.models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'video',
            'video_id',
            'video_duration',
            'module',
            'course',
            'order',
        ]
        extra_kwargs = {
            'order': {'required': False}
        }
