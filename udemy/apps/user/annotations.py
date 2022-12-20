from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class UserAnnotations(AnnotationBase):
    def num_subscribed_courses(self):
        return models.Count('enrolled_courses', distinct=True)

    def subscribed_courses(self):
        return ArrayAgg('enrolled_courses__id', filter=~models.Q(enrolled_courses=None))
