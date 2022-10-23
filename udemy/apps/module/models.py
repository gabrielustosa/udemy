from django.db import models
from django.utils.translation import gettext_lazy as _

from udemy.apps.core.fields import OrderField
from udemy.apps.course.models import Course


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE
    )
    title = models.CharField(_('Title'), max_length=200)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'
