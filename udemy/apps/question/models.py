from django.db import models

from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.lesson.models import Lesson
from udemy.apps.user.models import User


class Question(CreatorBase, TimeStampedBase):
    lesson = models.ForeignKey(
        Lesson,
        related_name='questions',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    liked_by = models.ManyToManyField(
        User,
        related_name='questions_liked',
        blank=True
    )

    def __str__(self):
        return self.title


class Answer(CreatorBase, TimeStampedBase):
    question = models.ForeignKey(
        Question,
        related_name='answers',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    liked_by = models.ManyToManyField(
        User,
        related_name='answer_liked',
        blank=True
    )
