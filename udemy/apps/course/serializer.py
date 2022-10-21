from rest_framework import serializers

from udemy.apps.course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline', 'language',
            'is_paid', 'price', 'created', 'modified',
            'categories', 'instructors',
        ]
        extra_kwargs = {
            'instructors': {'required': False},
            'categories': {'required': False},
        }

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course
