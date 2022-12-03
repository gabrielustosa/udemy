from rest_framework.viewsets import ModelViewSet

from udemy.apps.category.models import Category
from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.mixins.view import DynamicFieldViewMixin
from udemy.apps.core.permissions import IsAdminOrReadOnly


class CategoryViewSet(DynamicFieldViewMixin, ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
