from rest_framework import serializers

from udemy.apps.course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline',
            'is_paid', 'price', 'language', 'instructors',
        ]
        extra_kwargs = {
            'instructors': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course
