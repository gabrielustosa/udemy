from django.db import models

from udemy.apps.category.annotations import CategoryAnnotations


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    annotation_class = CategoryAnnotations()

    def __str__(self):
        return self.title
