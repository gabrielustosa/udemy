from collections import OrderedDict

from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from rest_framework.exceptions import PermissionDenied

from udemy.apps.core.annotations import QUERYSET_DELIMITER
from udemy.apps.core.paginator import PaginatorRelatedObject


class RelatedObjectAnnotationMixin:
    @property
    def related_objects_annotations(self):
        related_object_annotations = {}
        for field_name, fields in self.related_objects_fields.items():
            annotation_class = getattr(self.get_related_object_model(field_name), 'annotation_class', None)
            if not self.related_object_is_prefetch(field_name) and annotation_class is not None:
                annotation_fields = annotation_class.intersection_fields(fields)
                annotations = annotation_class.get_annotations(*annotation_fields, additional_path=field_name)
                related_object_annotations[field_name] = annotations
        return related_object_annotations

    def optimize_related_objects_annotations(self, queryset):
        for annotations in self.related_objects_annotations.values():
            queryset = queryset.annotate(**annotations)
        return queryset

    def to_representation(self, instance):
        for field_name, annotations in self.related_objects_annotations.items():
            related_instance = getattr(instance, field_name)

            for annotation_name in annotations.keys():
                annotation_value = getattr(instance, annotation_name)

                annotation_name = annotation_name.split(QUERYSET_DELIMITER)[-1]

                setattr(related_instance, annotation_name, annotation_value)

        return super().to_representation(instance)


class RelatedObjectMixin(RelatedObjectAnnotationMixin):

    @cached_property
    def related_objects_fields(self):
        related_fields = {}
        for field_name, fields in self.context.get('related_fields', {}).items():
            if field_name in self.related_objects():
                related_fields[field_name] = fields
        return related_fields

    def related_objects(self):
        return getattr(self.Meta, 'related_objects', {})

    def _get_related_object_option(self, related_object, option_name, default=None):
        options = self.related_objects().get(related_object)
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
        queryset = self.optimize_related_object_queryset(queryset)
        queryset = self.optimize_related_objects_annotations(queryset)
        return queryset

    def optimize_related_object_queryset(self, queryset):
        for field_name in self.related_objects_fields.keys():
            if self.related_object_is_prefetch(field_name):
                queryset = queryset.prefetch_related(field_name)
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

        for field_name, fields in self.related_objects_fields.items():
            self.check_related_object_permission(self.instance, field_name)

            Serializer = self.get_related_object_serializer(field_name)
            serializer_kwargs = {'fields': fields}

            if self.related_object_is_prefetch(field_name):
                serializer_kwargs.update({
                    'many': True,
                    'filter': self._get_related_object_option(field_name, 'filter'),
                    'paginator': PaginatorRelatedObject(
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
