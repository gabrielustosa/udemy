from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.module.serializer import ModuleSerializer
from udemy.apps.quiz.models import Quiz, Question


class QuizSerializer(ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description',
            'is_published', 'is_draft', 'is_timed',
            'pass_percent', 'module', 'order',
            'course', 'created', 'modified'
        ]
        related_objects = {
            'module': {
                'serializer': ModuleSerializer
            },
            'course': {
                'serializer': CourseSerializer
            },
            'questions': {
                'serializer': 'udemy.apps.quiz.serializer.QuestionSerializer',
                'many': True
            },
        }
        create_only_fields = ('course', 'module')
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'description', 'module', 'course')
        permissions_for_field = {
            ('module', 'course'): [IsInstructor]
        }


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'question', 'feedback',
            'answers', 'max_time', 'quiz',
            'correct_response', 'order',
            'created', 'modified', 'course'
        ]
        related_objects = {
            'quiz': {
                'serializer': QuizSerializer
            },
            'course': {
                'serializer': CourseSerializer
            },
        }
        create_only_fields = ('course', 'quiz')
        min_fields = ('id', 'question')
        default_fields = (*min_fields, 'answers', 'correct_response')
        permissions_for_field = {
            ('course',): [IsInstructor]
        }
