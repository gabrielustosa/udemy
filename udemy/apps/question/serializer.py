from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.question.models import Question
from udemy.apps.user.serializer import UserSerializer


class QuestionSerializer(ModelSerializer):

    class Meta:
        model = Question
        fields = [
            'id', 'creator', 'lesson', 'title',
            'content', 'created', 'modified',
            'course',
        ]
        related_objects = {
            'creator': {
                'serializer': UserSerializer
            },
            'lesson': {
                'serializer': LessonSerializer
            },
            'course': {
                'serializer': CourseSerializer
            }
        }
        create_only_fields = ('course', 'lesson')
        min_fields = ('id', 'title', 'content')
        default_fields = (*min_fields, 'creator', 'course')
        permissions_for_field = {
            ('lesson', 'course'): [IsEnrolled],
        }
