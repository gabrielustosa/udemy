from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

from udemy.apps.action.models import Action
from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course


class Answer(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(1000)
        ])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    actions = GenericRelation(Action)
