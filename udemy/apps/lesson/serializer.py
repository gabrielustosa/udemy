from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.models import Lesson, LessonRelation
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
            'course': {
                'serializer': CourseSerializer
            },
            'module': {
                'serializer': ModuleSerializer,
            },
            'contents': {
                'serializer': 'udemy.apps.content.serializer.ContentSerializer',
            },
            'questions': {
                'serializer': 'udemy.apps.question.serializer.QuestionSerializer',
            },
            'notes': {
                'serializer': 'udemy.apps.note.serializer.NoteSerializer',
            }
        }
        create_only_fields = ('course', 'module')
        read_only_fields = ('video_duration', 'video_id')
        update_only_fields = ('order',)
        min_fields = ('id', 'title', 'video')
        default_fields = (*min_fields, 'video_id', 'video_duration')
        permissions_for_field = {
            ('module', 'course'): [IsInstructor],
        }

        def get_related_objects(self):
            related_objects = super().get_related_objects()
            if self.context.get('request'):
                related_objects['notes']['filter'] = {
                    'creator': self.context.get('request').user
                }
            return related_objects


class LessonRelationSerializer(ModelSerializer):
    class Meta:
        model = LessonRelation
        fields = ('creator', 'lesson', 'course', 'done', 'created', 'modified')
        min_fields = ('creator', 'lesson', 'done')
        default_fields = (*min_fields, 'course')
