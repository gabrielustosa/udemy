from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

from udemy.apps.answer.models import Answer
from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course


class Message(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(
        Course,
        related_name='warning_messages',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(3)
        ])
    content = models.TextField(
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(1000)
        ])
    answers = GenericRelation(Answer)
