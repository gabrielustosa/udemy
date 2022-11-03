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
    content_types = {
        models.Link: LinkSerializer(),
        models.Text: TextSerializer(),
        models.File: FileSerializer(),
        models.Image: ImageSerializer()
    }
    item = GenericRelatedField(content_types)

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

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        if 'item' in ret:
            item = ret.pop('item')
            Model = self.get_model_for_data(item)

            item = Model.objects.create(**item)

            ret['item'] = item

        return ret

    def get_model_for_data(self, data):
        object_model = None
        for model, serializer in self.content_types.items():
            try:
                result = serializer.to_internal_value(data)
                if bool(result):
                    object_model = model
            except Exception:
                pass
        return object_model
