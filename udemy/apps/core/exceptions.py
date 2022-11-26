from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def django_error_handler(exc, context):
    """Handle django core's errors."""
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, ValidationError):
        return Response(data=exc.message_dict, status=status.HTTP_400_BAD_REQUEST)
    if response is None and isinstance(exc, IntegrityError):
        if 'duplicate key value' in exc.args[0]:
            return Response(data={'Duplicate object.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'Database integrity error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
