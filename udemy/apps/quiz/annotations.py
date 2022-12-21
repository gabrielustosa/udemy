from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class QuizAnnotations(AnnotationBase):
    def num_questions(self):
        return models.Count('questions', distinct=True)
