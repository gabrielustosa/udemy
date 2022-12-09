from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

from udemy.apps.action.models import Action
from udemy.apps.answer.models import Answer
from udemy.apps.core.annotations import AnnotationBase
from udemy.apps.core.decorator import annotation_field
from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson
from udemy.apps.question.annotations import QuestionAnnotations


class Question(CreatorBase, TimeStampedBase, AnnotationBase):
    lesson = models.ForeignKey(
        Lesson,
        related_name='questions',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='questions',
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
    actions = GenericRelation(Action)
    answers = GenericRelation(Answer)
    annotation_class = QuestionAnnotations
    annotations_fields = ('likes_count', 'dislikes_count')

    @annotation_field()
    def likes_count(self):
        return self.actions.filter(action=1).count()

    @annotation_field()
    def dislikes_count(self):
        return self.actions.filter(action=2).count()

    def __str__(self):
        return self.title
