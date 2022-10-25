from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.db import models
from django.db.models import Max, F, ExpressionWrapper, PositiveIntegerField
from django.utils.translation import gettext_lazy as _


class UrlBase(models.Model):
    def get_url(self):
        if hasattr(self.get_url_path, "dont_recurse"):
            raise NotImplementedError
        try:
            path = self.get_url_path()
        except NotImplementedError:
            raise
        return settings.WEBSITE_URL + path

    get_url.dont_recurse = True

    def get_url_path(self):
        if hasattr(self.get_url, "dont_recurse"):
            raise NotImplementedError
        try:
            url = self.get_url()
        except NotImplementedError:
            raise
        bits = urlparse(url)
        return urlunparse(("", "") + bits[2:])

    get_url_path.dont_recurse = True

    def get_absolute_url(self):
        return self.get_url()

    class Meta:
        abstract = True


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
        from .middleware import get_current_user

        if not self.creator:
            self.creator = get_current_user()
        super().save(*args, **kwargs)

    save.alters_data = True


class OrderedModel(models.Model):
    order_in_respect = None
    order = models.PositiveIntegerField(null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, instance):
        query = {field: getattr(instance, field) for field in instance.order_in_respect}
        return cls.objects.filter(**query)

    def get_last_order(self):
        last_order = self.get_queryset(instance=self).aggregate(ls=Max('order'))['ls']
        return last_order if last_order else 0

    def get_next_order(self):
        return self.get_last_order() + 1

    def do_after_update(self):
        return None

    def do_after_create(self):
        return None

    def save(self, force_insert=False, **kwargs):
        if force_insert:
            order = self.get_next_order()
            setattr(self, 'order', order)

            self.do_after_create()
        else:
            current_order = self.get_queryset(self).filter(id=self.id).first().order
            new_order = self.order

            number, query = (1, {'order__gte': new_order, 'order__lte': current_order}) if current_order > new_order \
                else (-1, {'order__lte': new_order, 'order__gte': current_order})

            self.get_queryset(self).filter(**query).update(
                order=ExpressionWrapper(F('order') + number, output_field=PositiveIntegerField()))

            self.do_after_update()

        return super().save(force_insert, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.get_queryset(self).filter(order__gt=self.order).update(
            order=ExpressionWrapper(F('order') - 1, output_field=models.PositiveIntegerField()))
        return super().delete(using, keep_parents)
