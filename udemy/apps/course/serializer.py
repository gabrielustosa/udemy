from rest_framework import serializers

from udemy.apps.course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline',
            'is_paid', 'price', 'language',
        ]
