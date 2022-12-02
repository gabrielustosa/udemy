from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, F, ExpressionWrapper, PositiveIntegerField
from django.utils.translation import gettext_lazy as _


class TimeStampedBase(models.Model):
    created = models.DateTimeField(
        _("Creation Date and Time"),
        auto_now_add=True,
    )

    modified = models.DateTimeField(
        _("Modification Date and Time"),
        auto_now=True,
    )

    class Meta:
        abstract = True


class CreatorBase(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("creator"),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from udemy.apps.core.middleware import get_current_user

        if not self.creator:
            self.creator = get_current_user()
        super().save(*args, **kwargs)

    save.alters_data = True


class OrderedModel(models.Model):
    order_in_respect = None
    order = models.PositiveIntegerField(null=True)

    class Meta:
        abstract = True
        ordering = ('order',)

    def get_queryset(self):
        query = {field: getattr(self, field) for field in self.order_in_respect}
        return self.__class__.objects.filter(**query)

    def get_last_order(self):
        last_order = self.get_queryset().aggregate(ls=Max('order'))['ls']
        return last_order if last_order else 0

    def get_next_order(self):
        return self.get_last_order() + 1

    def do_after_update(self):
        return None

    def do_after_create(self):
        return None

    def save(self, force_insert=False, **kwargs):
        if force_insert:
            self.order = self.get_next_order()

            self.do_after_create()
        else:
            new_order = self.order

            if new_order > self.get_last_order():
                raise ValidationError('The order can not be greater than last order of the object.')

            current_order = self.get_queryset().filter(id=self.id).first().order

            number, query = (1, {'order__gte': new_order, 'order__lte': current_order}) if current_order > new_order \
                else (-1, {'order__lte': new_order, 'order__gte': current_order})

            self.get_queryset().filter(**query).update(
                order=ExpressionWrapper(F('order') + number, output_field=PositiveIntegerField()))

            self.do_after_update()
        super().save(force_insert, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.get_queryset().filter(order__gt=self.order).update(
            order=ExpressionWrapper(F('order') - 1, output_field=models.PositiveIntegerField()))
        return super().delete(using, keep_parents)


class ModelTest(models.Model):
    title = models.CharField(max_length=100)
    num = models.PositiveIntegerField(default=0)


class ModelRelatedObject(models.Model):
    title = models.CharField(max_length=100)
    model_test = models.ForeignKey(
        ModelTest,
        on_delete=models.CASCADE,
        related_name='model_related'
    )
