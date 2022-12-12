from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class CourseAnnotations(AnnotationBase):

    def num_modules(self):
        return {
            'expression': models.Count,
            'query_expression': 'modules',
        }

    def num_lessons(self):
        return {
            'expression': models.Count,
            'query_expression': 'lessons'
        }

    def num_contents(self):
        return {
            'expression': models.Count,
            'query_expression': 'contents'
        }

    def num_subscribers(self):
        return {
            'expression': models.Count,
            'query_expression': 'students'
        }

    def num_contents_info(self):
        return [{
            'annotation_name': f'num_{option}',
            'expression': models.Count,
            'query_expression': 'contents__id',
            'filter_expressions': {'contents__content_type__model': option},
        } for option in ('text', 'link', 'file', 'image')]

    def rating_avg(self):
        return {
            'expression': models.Avg,
            'query_expression': 'ratings__rating',
            'extra_kwargs': {
                'output_field': models.FloatField()
            }
        }

    def estimated_content_length_video(self):
        return {
            'expression': models.Sum,
            'query_expression': 'lessons__video_duration',
            'extra_kwargs': {
                'output_field': models.IntegerField()
            }
        }
