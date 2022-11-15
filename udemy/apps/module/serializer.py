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
        update_only_fields = ('order',)
