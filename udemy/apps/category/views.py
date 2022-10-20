from rest_framework.viewsets import ModelViewSet

from udemy.apps.category.models import Category
from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.permissions import IsAdminOrReadOnly


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
