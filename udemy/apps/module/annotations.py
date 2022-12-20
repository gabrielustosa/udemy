from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class ModuleAnnotations(AnnotationBase):
    def num_lessons(self):
        return models.Count('lessons', distinct=True)
