from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class CourseAnnotations(AnnotationBase):

    def num_modules(self):
        return models.Count('modules', distinct=True)

    def num_lessons(self):
        return models.Count('lessons', distinct=True)

    def num_contents(self):
        return models.Count('contents', distinct=True)

    def num_subscribers(self):
        return models.Count('students', distinct=True)

    def num_questions(self):
        return models.Count('questions', distinct=True)

    def num_quizzes(self):
        return models.Count('quizzes', distinct=True)

    def num_ratings(self):
        return models.Count('ratings', distinct=True)

    def num_contents_info(self):
        return {
            f'num_{option}': models.Count('contents__id', filter=models.Q(contents__content_type__model=option))
            for option in ('text', 'link', 'file', 'image')
        }

    def rating_avg(self):
        return models.Avg('ratings__rating', default=0)

    def content_video_minute_duration(self):
        return models.Sum('lessons__video_duration', output_field=models.IntegerField(), default=0)
