from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveNestedObjectMixin
from udemy.apps.core.permissions import IsCreatorObject, IsEnrolled
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer


class RatingViewSet(RetrieveNestedObjectMixin, ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCreatorObject, IsEnrolled]

    def create(self, request, *args, **kwargs):
        user_already_rated = Rating.objects.filter(creator=request.user, course=request.data['course']).exists()
        if user_already_rated:
            return Response({'rating': 'You have already rated this course.'}, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
