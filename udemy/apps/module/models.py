from django.db import models
from django.utils.translation import gettext_lazy as _

from udemy.apps.core.models import OrderedModel
from udemy.apps.course.models import Course
from udemy.apps.module.annotations import ModuleAnnotations


class Module(OrderedModel):
    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE,
    )
    title = models.CharField(_('Title'), max_length=200)
    order_in_respect = ('course',)
    annotation_class = ModuleAnnotations()

    def __str__(self):
        return f'{self.order}. {self.title}'
