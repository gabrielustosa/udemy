from rest_framework import generics

from udemy.apps.user.api.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
