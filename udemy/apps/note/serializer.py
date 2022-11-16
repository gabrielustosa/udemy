from udemy.apps.core.fields import ModelSerializer
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
        min_fields = ('id', 'note')
        default_fields = (*min_fields, 'creator', 'lesson', 'time')
