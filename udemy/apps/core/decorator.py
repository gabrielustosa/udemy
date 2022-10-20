from rest_framework.response import Response

from utils.module import import_name


def componentize(result_name='result', component_class=None):
    def decorator(func):
        def inner(self, request, *args, **kwargs):
            nonlocal component_class

            old_response = func(self, request, *args, **kwargs)
            response = {
                result_name: old_response.data,
            }

            if not component_class:
                component_class = f"{'.'.join(self.__module__.split('.')[0:-1])}.components"

            components = request.query_params.get('components', None)
            if components:
                for component in components.split(','):
                    function = import_name(component_class, component)
                    if not function:
                        continue
                    response.update({
                        component: function(**kwargs)
                    })
            return Response(response, status=old_response.status_code)

        return inner

    return decorator
