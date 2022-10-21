from rest_framework import serializers

from udemy.apps.rating.models import Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            'id', 'course', 'rating', 'comment',
            'creator', 'created', 'modified',
        ]
        extra_kwargs = {
            'creator': {'read_only': True},
            'course': {'read_only': True},
        }

    def validate(self, attrs):
        if attrs['rating'] < 1 or attrs['rating'] > 5:
            raise serializers.ValidationError('Rating must between 1 and 5.')
        return attrs
