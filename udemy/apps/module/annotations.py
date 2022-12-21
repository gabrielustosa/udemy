from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class ModuleAnnotations(AnnotationBase):
    def num_lessons(self):
        return models.Count('lessons', distinct=True)

    def num_quizzes(self):
        return models.Count('quizzes', distinct=True)

    def content_video_minute_duration(self):
        return models.Sum('lessons__video_duration', output_field=models.IntegerField(), default=0)
