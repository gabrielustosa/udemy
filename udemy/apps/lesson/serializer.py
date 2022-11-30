from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled, IsInstructor
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
            'course': CourseSerializer,
            'contents': 'udemy.apps.content.serializer.ContentSerializer',
            'questions': 'udemy.apps.question.serializer.QuestionSerializer'
        }
        related_objects_permissions = {
            ('contents', 'questions'): [IsEnrolled],
        }
        create_only_fields = ('course', 'module')
        read_only_fields = ('video_duration', 'video_id')
        update_only_fields = ('order',)
        min_fields = ('id', 'title', 'video')
        default_fields = (*min_fields, 'video_id', 'video_duration')
        permissions_for_field = {
            ('module', 'course'): [IsInstructor],
        }
