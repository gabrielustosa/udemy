from rest_framework import serializers

from udemy.apps.core.mixins import serializer
from udemy.apps.core.mixins.related_object import RelatedObjectMixin


class ModelSerializer(
    RelatedObjectMixin,
    serializer.DynamicModelFieldsMixin,
    serializer.CreateAndUpdateOnlyFieldsMixin,
    serializer.PermissionForFieldMixin,
    serializer.AnnotationFieldMixin,
    serializers.ModelSerializer,
):
    """
    Custom ModelSerializer
    """
