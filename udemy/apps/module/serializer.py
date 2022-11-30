from udemy.apps.core.serializer import ModelSerializer
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
            'course': {
                'serializer': CourseSerializer
            },
            'lessons': {
                'serializer': 'udemy.apps.lesson.serializer.LessonSerializer',
            },
            'quizzes': {
                'serializer': 'udemy.apps.quiz.serializer.QuizSerializer',
                'filter': {'is_published': True}
            }
        }
        create_only_fields = ('course',)
        update_only_fields = ('order',)
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'course')
        permissions_for_field = {
            ('course',): [IsInstructor]
        }
