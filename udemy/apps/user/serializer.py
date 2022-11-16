from django.contrib.auth import get_user_model
from rest_framework import serializers

from udemy.apps.core.fields import ModelSerializer


class UserSerializer(ModelSerializer):
    num_subscribed_courses = serializers.SerializerMethodField()
    subscribed_courses = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'password', 'name',
            'first_name', 'last_name',
            'job_title', 'is_active',
            'locale', 'bio', 'date_joined',
            'num_subscribed_courses', 'subscribed_courses',
        ]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        min_fields = ('id', 'name')
        default_fields = (*min_fields, 'first_name', 'last_name', 'locale')

    def get_num_subscribed_courses(self, instance):
        return instance.enrolled_courses.count()

    def get_subscribed_courses(self, instance):
        return instance.enrolled_courses.values_list('id', flat=True)

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
