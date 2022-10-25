from rest_framework import serializers

from udemy.apps.content.models import Content


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'id',
            'title',
            'lesson',
            'order',
        ]
        extra_kwargs = {
            'order': {'required': False},
        }
