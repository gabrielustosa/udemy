from udemy.apps.core.serializers.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled, IsInstructor
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.module.models import Module


class ModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = [
            'id',
            'title',
            'order',
            'course'
        ]
        related_objects = {
            'course': CourseSerializer,
            'lessons': ('udemy.apps.lesson.serializer', 'LessonSerializer'),
            'quizzes': ('udemy.apps.quiz.serializer', 'QuizSerializer'),
        }
        related_objects_permissions = {
            ('lessons', 'quizzes'): [IsEnrolled],
        }
        create_only_fields = ('course',)
        update_only_fields = ('order',)
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'course')
        permissions_for_field = {
            ('course',): [IsInstructor]
        }
