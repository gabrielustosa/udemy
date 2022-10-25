from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from udemy.apps.content.models import Content
from udemy.apps.content.serializer import ContentSerializer
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.lesson.models import Lesson
from utils.utils import content_model_types, get_model


class ContentViewSet(ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]

    def create(self, request, *args, **kwargs):
        if 'order' in request.data:
            return Response({'order': 'Order is automatically generated.'}, status.HTTP_400_BAD_REQUEST)

        if 'model' not in request.data:
            return Response({'model': 'You must provide a content model name.'}, status.HTTP_400_BAD_REQUEST)

        model_name = request.data['model']

        if model_name not in content_model_types:
            return Response({'content_type': f'Valid content types are {", ".join(content_model_types.keys())}'},
                            status.HTTP_400_BAD_REQUEST)

        content_type = content_model_types.get(model_name)

        if content_type not in request.data:
            return Response({'content_type': f"You must provide a '{content_type}' field."}, status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = get_model(model_name)
        item = model.objects.create(**{content_type: request.data[content_type]})

        lesson = Lesson.objects.filter(id=request.data['lesson']).first()
        content = Content.objects.create(lesson=lesson, course=lesson.course, title=request.data['title'], item=item)

        data = {**serializer.data, 'order': content.order, 'model': model_name,
                content_type: request.data[content_type]}

        return Response(data, status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        content = self.get_object()
        model_name = content.content_type.model
        content_type = content_model_types.get(model_name)

        new_data = {content_type: getattr(content.item, content_type)}

        if content_type in request.data:
            field_value = request.data[content_type]
            new_data[content_type] = field_value
            item = content.item
            setattr(item, content_type, field_value)
            item.save()

        response = super().update(request, *args, **kwargs)

        return Response({**response.data, **new_data}, response.status_code)

    def retrieve(self, request, *args, **kwargs):

        content = self.get_object()

        model_name = content.content_type.model
        content_type = content_model_types.get(model_name)

        serializer = self.get_serializer(content)

        data = {**serializer.data, 'model': model_name, content_type: getattr(content.item, content_type)}

        return Response(data)
