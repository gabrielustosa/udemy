from udemy.apps.core.fields import ModelSerializer
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
            'course': CourseSerializer
        }
        create_only_fields = ('course',)
        update_only_fields = ('order',)
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'course')
