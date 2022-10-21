from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.decorator import componentize
from udemy.apps.core.permissions import IsInstructor
from udemy.apps.course.models import Course
from udemy.apps.course.serializer import CourseSerializer


class CoursePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInstructor]
    pagination_class = CoursePagination

    @componentize(result_name='details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @componentize(result_name=None)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

# class AddCategoriesAPIView(GenericAPIView):
#     permission_classes = [IsInstructor]
#
#     def post(self, request, *args, **kwargs):
#         course = Course.objects.filter(id=kwargs.get('course_id')).first()
#         if not course:
#             return Response({'detail': 'Course not found.'}, status.HTTP_404_NOT_FOUND)
#
#         categories_id = request.data.get('categories')
#
#         categories = Category.objects.filter(id__in=categories_id)
#
#         if not categories:
#             return Response({'detail': 'Category not found.'}, status.HTTP_404_NOT_FOUND)
#
#         course.categories.add(*[category.id for category in categories])
#
#         serializer = CourseSerializer(course)
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
