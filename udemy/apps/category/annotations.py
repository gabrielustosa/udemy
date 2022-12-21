from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models

from udemy.apps.core.annotations import AnnotationBase


class CategoryAnnotations(AnnotationBase):
    def courses(self):
        return ArrayAgg('categories_courses__id', filter=~models.Q(categories_courses=None))
