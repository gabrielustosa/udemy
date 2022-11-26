from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from udemy.apps.core.models import TimeStampedBase, OrderedModel, CreatorBase
from udemy.apps.course.models import Course
from udemy.apps.module.models import Module


class Quiz(TimeStampedBase, OrderedModel):
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    is_published = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_timed = models.BooleanField(default=False)
    pass_percent = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    module = models.ForeignKey(
        Module,
        related_name='quizzes',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='quizzes',
        on_delete=models.CASCADE,
    )
    order_in_respect = ('course', 'module')


class Question(TimeStampedBase, OrderedModel):
    question = models.TextField()
    feedback = models.TextField()
    answers = ArrayField(models.TextField())
    max_time = models.PositiveIntegerField(default=0)
    quiz = models.ForeignKey(
        Quiz,
        related_name='questions',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name='questions_quiz',
        on_delete=models.CASCADE,
    )
    correct_response = models.IntegerField(validators=[MinValueValidator(1)])
    order_in_respect = ('quiz',)

    def save(self, *args, **kwargs):
        if self.correct_response > len(self.answers):
            raise ValidationError({'correct_response': 'invalid response'})
        super().save(*args, **kwargs)


class QuizRelation(CreatorBase, TimeStampedBase):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('creator', 'quiz'), name='unique quiz relation')]
