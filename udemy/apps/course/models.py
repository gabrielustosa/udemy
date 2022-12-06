from django.db import models
from django.db.models import Count, Avg, Q, Sum
from django.utils.translation import gettext_lazy as _

from udemy.apps.category.models import Category
from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.user.models import User


class Course(TimeStampedBase):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(unique=True)
    headline = models.TextField(_('Headline'))
    description = models.TextField(_('Description'))
    is_paid = models.BooleanField(_('Is paid'))
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    language = models.CharField(_('Language'), max_length=155)
    requirements = models.TextField(_('Requirements'))
    what_you_will_learn = models.TextField(_('What you will learn'))
    level = models.TextField(_('Course Level'))
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

    @staticmethod
    def get_num_modules():
        return {'num_modules': Count('modules')}

    @staticmethod
    def get_num_lessons():
        return {'num_lessons': Count('lessons')}

    @staticmethod
    def get_num_contents():
        return {'num_contents': Count('contents')}

    @staticmethod
    def get_avg_rating():
        return {'avg_rating': Avg('ratings__rating')}

    @staticmethod
    def get_num_subscribers():
        return {'num_subscribers': Count('students')}

    @staticmethod
    def get_num_contents_info():
        return {f'content_num_{option}': Count('contents__id', filter=Q(contents__content_type__model=option))
                for option in ['text', 'link', 'file', 'image']}

    @staticmethod
    def get_estimated_content_length_video():
        return {'estimated_content_length_video': Sum('lessons__video_duration')}


class CourseRelation(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('creator', 'course'), name='unique course relation')]
