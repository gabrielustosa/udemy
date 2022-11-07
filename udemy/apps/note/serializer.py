from rest_framework import serializers

from udemy.apps.note.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id',
            'creator',
            'course',
            'lesson',
            'time',
            'note',
            'modified',
            'created'
        ]
