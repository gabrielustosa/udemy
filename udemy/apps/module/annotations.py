from django.db.models import Count

from udemy.apps.core.annotations import AnnotationBase


class ModuleAnnotations(AnnotationBase):
    def num_lessons(self):
        return {
            'expression': Count,
            'query_expression': 'lessons',
            'extra_kwargs': {
                'distinct': True
            }
        }
