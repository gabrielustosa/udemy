from django.db import models
from django.db.models import Avg, Sum, Count, Q
from django.utils.translation import gettext_lazy as _

from udemy.apps.category.models import Category
from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.course.annotations import CourseAnnotations
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
    annotation_class = CourseAnnotations
    annotations_fields = (
        'num_modules', 'num_lessons', 'num_contents',
        'avg_rating', 'estimated_content_length_video',
        'num_contents_info',
    )

    @staticmethod
    def get_annotations(*fields):
        annotations = {}
        for field in fields:
            annotations.update(getattr(Course.annotation_class, f'get_{field}')())
        return annotations

    @property
    def num_modules(self):
        if not hasattr(self, '_num_modules'):
            return self.modules.count()
        return self._num_modules

    @property
    def num_lessons(self):
        if not hasattr(self, '_num_lessons'):
            return self.lessons.count()
        return self._num_lessons

    @property
    def num_contents(self):
        if not hasattr(self, '_num_contents'):
            return self.contents.count()
        return self._num_contents

    @property
    def avg_rating(self):
        if not hasattr(self, '_avg_rating'):
            return self.ratings.aggregate(avg=Avg('rating'))['avg']
        return self._avg_rating

    @property
    def num_subscribers(self):
        if not hasattr(self, '_num_subscribers'):
            return self.students.count()
        return self._num_subscribers

    @property
    def estimated_content_length_video(self):
        if not hasattr(self, '_estimated_content_length_video'):
            return self.lessons.aggregate(length=Sum('video_duration'))['length']
        return self._estimated_content_length_video

    @property
    def num_contents_info(self):
        if not hasattr(self, '_content_num_text'):
            return self.contents.aggregate(
                **{option: Count('id', filter=Q(content_type__model=option))
                   for option in ['text', 'link', 'file', 'image']},
            )
        return {
            'text': self._content_num_text,
            'link': self._content_num_link,
            'file': self._content_num_file,
            'image': self._content_num_image,
        }

    def __str__(self):
        return self.title


class CourseRelation(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('creator', 'course'), name='unique course relation')]
