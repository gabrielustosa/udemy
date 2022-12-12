from django.db.models import Count

from udemy.apps.core.annotations import AnnotationBase


class ActionAnnotations(AnnotationBase):

    def likes_count(self):
        return {
            'expression': Count,
            'query_expression': 'actions__id',
            'filter_expression': {'actions__action': 1},
        }

    def dislikes_count(self):
        return {
            'expression': Count,
            'query_expression': 'actions__id',
            'filter_expression': {'actions__action': 2},
        }
