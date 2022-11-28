from rest_framework import serializers

from udemy.apps.core.serializers import mixins


class ModelSerializer(
    mixins.DynamicModelFieldsMixin,
    mixins.RelatedObjectMixin,
    mixins.CreateAndUpdateOnlyFieldsMixin,
    mixins.PermissionForFieldMixin,
    serializers.ModelSerializer
):
    """
    Custom ModelSerializer
    """
