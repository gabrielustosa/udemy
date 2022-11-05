from django.db import models
from django.utils.translation import gettext_lazy as _

from udemy.apps.action.models import Action
from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course


class Rating(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(
        Course,
        related_name='ratings',
        on_delete=models.CASCADE
    )
    rating = models.FloatField(verbose_name=_('Rating'))
    comment = models.TextField(_('Comment'))
    action = models.ManyToManyField(Action)

    class Meta:
        ordering = ['created', ]

    def __str__(self):
        return f'{self.creator} - {self.rating}'
