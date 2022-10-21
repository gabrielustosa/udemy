from udemy.apps.core.decorator import component
from udemy.apps.core.permissions import IsInstructor


@component()
def do_something(request, *args, **kwargs):
    return {'teste': True}


@component()
def do_other(request, *args, **kwargs):
    return {'other': -1}


@component(permission_classes=[IsInstructor])
def do_might(request, *args, **kwargs):
    return {'other': kwargs}
