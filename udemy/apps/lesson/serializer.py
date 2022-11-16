from udemy.apps.core.fields import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.models import Lesson
from udemy.apps.module.serializer import ModuleSerializer


class LessonSerializer(ModelSerializer):
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
        related_objects = {
            'module': ModuleSerializer,
            'course': CourseSerializer
        }
        update_only_fields = ('order',)
        min_fields = ('id', 'title', 'video')
        default_fields = (*min_fields, 'video_id', 'video_duration')
