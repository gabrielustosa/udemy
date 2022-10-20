from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from udemy.apps.user.serializer import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class A(APIView):
    """API TESTE"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'ola': 1, 'seu_nome': self.request.user.name})
