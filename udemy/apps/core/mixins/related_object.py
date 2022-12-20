from collections import OrderedDict

from django.db.models import Prefetch
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from rest_framework.exceptions import PermissionDenied

from udemy.apps.core.fields import RelatedObjectListSerializer
from udemy.apps.core.paginator import RelatedObjectPaginator


class RelatedObjectMixin:

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls(fields=kwargs.pop('fields', None))
        return RelatedObjectListSerializer(*args, **kwargs)

    @cached_property
    def related_objects_annotations(self):
        annotations = {}
        for field_name, fields in self.related_objects.items():
            annotation_class = getattr(self.get_related_object_model(field_name), 'annotation_class', None)
            if annotation_class is not None:
                annotations[field_name] = annotation_class.get_annotations(*fields)
        return annotations

    @cached_property
    def related_objects(self):
        related_fields = {}
        for field_name, fields in self.context.get('related_fields', {}).items():
            if field_name in self.get_related_objects():
                related_fields[field_name] = fields
        return related_fields

    def get_related_objects(self):
        return getattr(self.Meta, 'related_objects', {})

    def _get_related_object_option(self, related_object, option_name, default=None):
        options = self.get_related_objects().get(related_object)
        return options.get(option_name, default)

    def get_related_object_serializer(self, related_object):
        serializer = self._get_related_object_option(related_object, 'serializer')
        if isinstance(serializer, str):
            serializer = import_string(serializer)
        return serializer

    def check_related_object_permission(self, obj, related_object_name):
        permissions = self._get_related_object_option(related_object_name, 'permissions', [])

        request = self.context.get('request')
        view = self.context.get('view')
        for permission in [permission() for permission in permissions]:
            if not permission.has_object_permission(request, view, obj):
                raise PermissionDenied(
                    detail=f'You do not have permission to access the related object `{related_object_name}`'
                )

    def auto_optimize_related_object(self, queryset):
        for field_name in self.related_objects.keys():
            model_annotations = self.related_objects_annotations.get(field_name)
            if model_annotations:
                queryset = queryset.prefetch_related(Prefetch(
                    field_name,
                    self.get_related_object_model(field_name).objects.annotate(**model_annotations).order_by('id')
                ))
                continue
            if self.related_object_is_prefetch(field_name):
                queryset = queryset.prefetch_related(
                    Prefetch(field_name, self.get_related_object_model(field_name).order_by('id'))
                )
            else:
                queryset = queryset.select_related(field_name)
        return queryset

    def get_related_object_model(self, field_name):
        serializer = self.get_related_object_serializer(field_name)
        return serializer.Meta.model

    def related_object_is_prefetch(self, field_name):
        return self._get_related_object_option(field_name, 'many', False)

    def _get_related_objects_fields(self):
        related_objects_fields = OrderedDict()

        for field_name, fields in self.related_objects.items():
            self.check_related_object_permission(self.instance, field_name)

            Serializer = self.get_related_object_serializer(field_name)
            serializer_kwargs = {'fields': fields}

            if self.related_object_is_prefetch(field_name):
                serializer_kwargs.update({
                    'many': True,
                    'filter': self._get_related_object_option(field_name, 'filter'),
                    'paginator': RelatedObjectPaginator(
                        related_object_name=field_name,
                        related_object_fields=fields,
                        request=self.context.get('request')
                    )
                })

            related_objects_fields[field_name] = Serializer(**serializer_kwargs)

        return related_objects_fields

    def get_fields(self):
        fields = super().get_fields()

        fields.update(self._get_related_objects_fields())

        return fields
