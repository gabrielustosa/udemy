from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from udemy.apps.action.models import Action
from udemy.apps.answer.models import Answer
from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course
from udemy.apps.rating.annotations import RatingAnnotations


class Rating(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(
        Course,
        related_name='ratings',
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(
        verbose_name=_('Rating'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ])
    comment = models.TextField(_('Comment'))
    actions = GenericRelation(Action)
    answers = GenericRelation(Answer)
    annotation_class = RatingAnnotations()

    class Meta:
        ordering = ['created', ]
        constraints = [
            UniqueConstraint(fields=('creator', 'course'), name='unique rating',
                             violation_error_message='You already rated this course.')
        ]

    def __str__(self):
        return f'{self.creator} - {self.rating}'
