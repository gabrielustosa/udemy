from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from udemy.apps.core.models import TimeStampedBase, OrderedModel
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson


class Content(OrderedModel, TimeStampedBase):
    title = models.CharField(max_length=250)
    lesson = models.ForeignKey(
        Lesson,
        related_name='contents',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to={'model__in': (
            'text',
            'link',
            'image',
            'file')}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order_in_respect = ('lesson',)

    class Meta:
        ordering = ['order']


class Text(models.Model):
    content = models.TextField()


class File(models.Model):
    file = models.FileField(upload_to='files')


class Image(models.Model):
    image = models.ImageField(upload_to='images')


class Link(models.Model):
    url = models.URLField()
