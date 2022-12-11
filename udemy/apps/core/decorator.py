from rest_framework import status
from rest_framework.response import Response

components_list = dict()


def componentize(result_name=None):
    """
    A decorator used to componentize an endpoint to accept query params with components name registered with @component
    that are retrieved and attached to the response.

    Example: http://127.0.0.1:8000/api/course/?components=do_something,do_other

    """

    def decorator(func):
        def inner(self, request, *args, **kwargs):
            old_response = func(self, request, *args, **kwargs)

            response = old_response.data

            if result_name:
                response = {
                    result_name: old_response.data,
                }

            components = request.query_params.get('components')
            if components:
                for component_name in components.split(','):
                    component = components_list.get(component_name)
                    if not component:
                        continue

                    permission_classes = component.permission_classes
                    if permission_classes:
                        for permission in permission_classes:
                            if not permission.has_object_permission(self, request, func, self.get_object()):
                                return Response(
                                    {'details': f'Access denied for component {component_name}'},
                                    status=status.HTTP_403_FORBIDDEN
                                )
                            if not permission.has_permission(self, request, func):
                                return Response(
                                    {'details': f'Access denied for component {component_name}'},
                                    status=status.HTTP_403_FORBIDDEN
                                )

                    response.update({
                        component_name: component(request, *args, **kwargs)
                    })
            return Response(response, status=old_response.status_code)

        return inner

    return decorator


def component(name=None, permission_classes=None):
    """
    A decorator used to transform a function in a component.
    """

    def decorator(func):
        nonlocal name
        if not name:
            name = func.__name__

        func.permission_classes = permission_classes

        components_list[name] = func

    return decorator


