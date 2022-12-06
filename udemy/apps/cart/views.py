from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from udemy.apps.cart.cart import Cart
from udemy.apps.course.models import Course


class CartView(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cart = Cart(request)

        data = cart.to_representation()

        return Response(data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        cart = Cart(request)

        course = get_object_or_404(Course, id=kwargs.get('course_id'))

        cart.add(course)

        return Response({'detail': 'success'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart = Cart(request)

        course = get_object_or_404(Course, id=kwargs.get('course_id'))

        cart.remove(course)

        return Response(status=status.HTTP_204_NO_CONTENT)
