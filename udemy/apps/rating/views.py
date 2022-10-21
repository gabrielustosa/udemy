from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsCreatorObject
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer


class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCreatorObject]

    def create(self, request, *args, **kwargs):
        user_is_enrolled = request.user.enrolled_courses.filter(id=request.data['course']).exists()
        if not user_is_enrolled:
            return Response({'detail': 'You are not enrolled in this course.'}, status.HTTP_403_FORBIDDEN)

        user_already_enrolled = Rating.objects.filter(creator=request.user, course=request.data['course']).exists()
        if user_already_enrolled:
            return Response({'detail': 'You have already rated this course.'}, status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)
