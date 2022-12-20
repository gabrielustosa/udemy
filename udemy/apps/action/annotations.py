from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class ActionAnnotations(AnnotationBase):

    def likes_count(self):
        return models.Count('actions__id', filter=models.Q(actions__action=1))

    def dislikes_count(self):
        return models.Count('actions__id', filter=models.Q(actions__action=2))
