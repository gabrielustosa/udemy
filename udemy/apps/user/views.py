from rest_framework import generics

from udemy.apps.user.serializer import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


