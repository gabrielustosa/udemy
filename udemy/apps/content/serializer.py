from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from udemy.apps.content import models


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
    content_models = {
        models.Link: LinkSerializer(),
        models.Text: TextSerializer(),
        models.File: FileSerializer(),
        models.Image: ImageSerializer()
    }
    item = GenericRelatedField(content_models)

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
        extra_kwargs = {
            'order': {'required': False},
        }

    def get_model_by_fields(self, fields):
        content_models = [model for model in self.content_models.keys()]
        for model in content_models:
            model_fields = [field.name for field in model._meta.get_fields() if field.name != 'id']
            if model_fields == list(fields):
                return model

    def create(self, validated_data):
        item = validated_data['item']
        model = self.get_model_by_fields(item.keys())
        validated_data['item'] = model.objects.create(**item)

        return super().create(validated_data)
