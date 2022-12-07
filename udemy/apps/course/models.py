from django.db import models
from django.db.models import Avg, Sum, Count, Q
from django.utils.translation import gettext_lazy as _

from udemy.apps.category.models import Category
from udemy.apps.core.decorator import annotation_field
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

    @classmethod
    def get_annotations(cls, *fields):
        annotations = {}
        for field in fields:
            annotations.update(getattr(cls.annotation_class, f'get_{field}')())
        return annotations

    @annotation_field()
    def num_modules(self):
        return self.modules.count()

    @annotation_field()
    def num_lessons(self):
        return self.lessons.count()

    @annotation_field()
    def num_contents(self):
        return self.contents.count()

    @annotation_field()
    def avg_rating(self):
        return self.ratings.aggregate(avg=Avg('rating'))['avg']

    @annotation_field()
    def num_subscribers(self):
        return self.students.count()

    @annotation_field()
    def estimated_content_length_video(self):
        return self.lessons.aggregate(length=Sum('video_duration'))['length']

    @annotation_field(field_group=['num_text', 'num_link', 'num_file', 'num_image'])
    def num_contents_info(self):
        return self.contents.aggregate(
            **{f'num_{option}': Count('id', filter=Q(content_type__model=option))
               for option in ['text', 'link', 'file', 'image']},
        )

    def __str__(self):
        return self.title


class CourseRelation(CreatorBase, TimeStampedBase):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('creator', 'course'), name='unique course relation')]
