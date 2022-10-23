from django.db import models
from django.db.models import ExpressionWrapper, F

from udemy.apps.course.models import Course
from udemy.apps.module.models import Module
from udemy.apps.user.models import User


class Lesson(models.Model):
    title = models.CharField(max_length=100)
    video = models.URLField()
    video_id = models.CharField(max_length=100)
    video_duration = models.FloatField()
    module = models.ForeignKey(
        Module,
        related_name='lessons',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        self.course.lessons.filter(order__gt=self.order).update(
            order=ExpressionWrapper(F('order') - 1, output_field=models.PositiveIntegerField()))
        return super().delete(using, keep_parents)


class LessonRelation(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    done = models.BooleanField(default=False)
