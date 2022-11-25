from django.db import models

from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson


class Note(CreatorBase, TimeStampedBase):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='notes',
        on_delete=models.CASCADE,
    )
    time = models.TimeField()
    note = models.TextField()
