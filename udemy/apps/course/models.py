from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from udemy.apps.category.models import Category
from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.user.models import User


class Course(TimeStampedBase):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True)
    headline = models.TextField(_('Headline'))
    is_paid = models.BooleanField(_('Is paid'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    language = models.CharField(_('Language'), max_length=155)
    requirements = models.TextField(_('Requirements'))
    what_you_will_learn = models.TextField(_('What you will learn'))
    instructors = models.ManyToManyField(
        User,
        related_name='instructors_courses',
    )
    students = models.ManyToManyField(
        User,
        related_name='enrolled_courses',
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

    min_fields = ()
    default_fields = ()

    def get_last_lesson_order(self):
        return self.lessons.aggregate(last_order=Max('order'))['last_order']


class CourseRelation(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    current_lesson = models.PositiveSmallIntegerField()
