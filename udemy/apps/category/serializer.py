from udemy.apps.category.models import Category
from udemy.apps.core.fields import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'title', 'slug'
        ]
