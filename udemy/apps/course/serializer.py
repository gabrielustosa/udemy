from rest_framework import serializers

from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.fields import ModelSerializer
from udemy.apps.course.models import Course, CourseRelation
from udemy.apps.user.serializer import UserSerializer


class CourseSerializer(ModelSerializer):
    instructors = UserSerializer(many=True, required=False)
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline', 'language',
            'is_paid', 'price', 'created', 'modified',
            'categories', 'instructors',
        ]

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course


class CourseRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRelation
        fields = [
            'id', 'creator', 'course',
            'modified', 'created', 'current_lesson',
        ]
        extra_kwargs = {
            'current_lesson': {'required': False}
        }
