from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.user.serializer import UserSerializer


class RatingSerializer(ModelSerializer):

    class Meta:
        model = Rating
        fields = [
            'id', 'course', 'rating', 'comment',
            'creator', 'created', 'modified',
        ]
        related_objects = {
            'creator': {
                'serializer': UserSerializer
            },
            'course': {
                'serializer': CourseSerializer
            }
        }
        create_only_fields = ('course',)
        min_fields = ('id', 'rating', 'comment')
        default_fields = (*min_fields, 'creator', 'course')
        permissions_for_field = {
            ('course',): [IsEnrolled]
        }


