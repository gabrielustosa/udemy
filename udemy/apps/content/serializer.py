from rest_framework import serializers

from udemy.apps.content import models
from udemy.apps.core.fields import GenericField


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Text
        fields = ('content',)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = ('file',)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('image',)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Link
        fields = ('url',)


class ContentSerializer(serializers.ModelSerializer):
    item = GenericField({
        models.Link: LinkSerializer(),
        models.Text: TextSerializer(),
        models.File: FileSerializer(),
        models.Image: ImageSerializer()
    })

    class Meta:
        model = models.Content
        fields = [
            'id',
            'title',
            'lesson',
            'course',
            'order',
            'item',
        ]
