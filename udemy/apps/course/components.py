from rest_framework.permissions import IsAuthenticated

from udemy.apps.core.decorator import component


@component()
def do_something(request, *args, **kwargs):
    return {'teste': True}


@component()
def do_other(request, *args, **kwargs):
    return {'other': -1}


@component(permission_classes=[IsAuthenticated])
def do_might(request, *args, **kwargs):
    return {'other': kwargs}
