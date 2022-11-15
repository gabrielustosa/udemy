from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsCreatorObject, IsEnrolled
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer


class RatingViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCreatorObject, IsEnrolled]

    class Meta:
        model = Rating
