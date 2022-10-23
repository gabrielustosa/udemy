from django.db.models import Max, F, ExpressionWrapper, PositiveIntegerField
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsInstructor
from udemy.apps.module.models import Module
from udemy.apps.module.serializer import ModuleSerializer


class ModuleViewSet(ModelViewSet):
    queryset = Module.objects.select_related('course').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    def create(self, request, *args, **kwargs):
        if 'order' in request.data:
            return Response({'detail': 'Order is automatically generated.'}, status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        if 'order' in request.data:
            course = self.get_object().course
            module_query = Module.objects.filter(course=course).order_by('order')
            last_order = module_query.aggregate(last_order=Max('order'))['last_order']
            new_order = int(request.data['order'])

            if new_order > last_order:
                return Response({'detail': 'The order can not be greater than last order of the module.'},
                                status.HTTP_400_BAD_REQUEST)

            current_order = self.get_object().order

            if current_order != new_order:
                if current_order > new_order:
                    # TODO Update lesson order
                    module_query.filter(order__gte=new_order, order__lt=current_order).update(
                        order=ExpressionWrapper(F('order') + 1, output_field=PositiveIntegerField()))
                else:
                    module_query.filter(order__lte=new_order, order__gt=current_order).update(
                        order=ExpressionWrapper(F('order') - 1, output_field=PositiveIntegerField()))

        return super().update(request, *args, **kwargs)
