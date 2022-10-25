from django.db import models
from django.db.models import Max, ExpressionWrapper, F, PositiveIntegerField

from udemy.apps.core.models import OrderedModel
from udemy.apps.course.models import Course
from udemy.apps.module.models import Module
from udemy.apps.user.models import User


class Lesson(OrderedModel):
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
    order_in_respect = ('module', 'module')

    class Meta:
        ordering = ['order']

    def get_next_order(self):
        queryset = self.get_queryset(self)
        if queryset.exists():
            last_lesson = queryset.aggregate(last_order=Max('order'))['last_order']
            order = last_lesson + 1
        else:
            last_lesson = self.course.get_last_lesson_order()

            if last_lesson:
                order = last_lesson + 1
            else:
                order = 1
        return order

    def do_after_create(self):
        self.course.lessons.filter(order__gte=self.order).update(
            order=ExpressionWrapper(F('order') + 1, output_field=PositiveIntegerField()))

    def __str__(self):
        return self.title


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
