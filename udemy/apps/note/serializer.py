from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.note.models import Note
from udemy.apps.user.serializer import UserSerializer


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id',
            'creator',
            'course',
            'lesson',
            'time',
            'note',
            'modified',
            'created'
        ]
        related_objects = {
            'creator': UserSerializer,
            'course': CourseSerializer,
            'lesson': LessonSerializer
        }
        create_only_fields = ('course', 'lesson')
        min_fields = ('id', 'note')
        default_fields = (*min_fields, 'creator', 'lesson', 'time')
        permissions_for_field = {
            ('lesson', 'course'): [IsEnrolled],
        }
