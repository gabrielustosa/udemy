from udemy.apps.core.fields import ModelSerializer
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
            'module': ModuleSerializer,
            'course': CourseSerializer
        }
        create_only_fields = ('course', 'module')
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'description', 'module', 'course')


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
            'quiz': QuizSerializer,
            'course': CourseSerializer,
        }
        create_only_fields = ('course', 'quiz')
        min_fields = ('id', 'question')
        default_fields = (*min_fields, 'answers', 'correct_response')
