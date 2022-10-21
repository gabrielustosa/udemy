from django.db import models
from django.utils.translation import gettext_lazy as _

from udemy.apps.category.models import Category
from udemy.apps.core.models import TimeStampedBase
from udemy.apps.user.models import User


class Course(TimeStampedBase):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True)
    headline = models.TextField(_('Headline'))
    is_paid = models.BooleanField(_('Is paid'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    language = models.CharField(_('Language'), max_length=155)
    instructors = models.ManyToManyField(
        User,
        related_name='instructors_courses',
    )
    students = models.ManyToManyField(
        User,
        related_name='students_courses',
        through='CourseRelation',
    )
    categories = models.ManyToManyField(
        Category,
        related_name='categories_courses',
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']


class CourseRelation(TimeStampedBase):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_lesson = models.PositiveSmallIntegerField()
