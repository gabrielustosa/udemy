from rest_framework import serializers

from udemy.apps.module.models import Module


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            'id',
            'title',
            'order',
            'course'
        ]
