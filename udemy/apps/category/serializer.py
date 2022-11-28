from udemy.apps.category.models import Category
from udemy.apps.core.serializers.serializer import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'title', 'slug'
        ]
        min_fields = ('id', 'title')
        default_fields = (*min_fields, 'slug')
