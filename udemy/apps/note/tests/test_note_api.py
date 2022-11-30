from datetime import datetime

from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.lesson import LessonFactory
from tests.factories.note import NoteFactory
from tests.factories.user import UserFactory

from udemy.apps.course.models import CourseRelation
from udemy.apps.note.models import Note
from udemy.apps.note.serializer import NoteSerializer

NOTE_LIST_URL = reverse('note-list')


def note_detail_url(pk): return reverse('note-detail', kwargs={'pk': pk})


class TestNoteAuthenticatedRequests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_note(self):
        lesson = LessonFactory()
        CourseRelation.objects.create(course=lesson.course, creator=self.user)

        payload = {
            'lesson': lesson.id,
            'course': lesson.course.id,
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.post(NOTE_LIST_URL, payload)

        note = Note.objects.get(id=response.data['id'])

        serializer = NoteSerializer(note)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_note_retrieve(self):
        note = NoteFactory(creator=self.user)
        CourseRelation.objects.create(course=note.course, creator=self.user)

        response = self.client.get(note_detail_url(note.id))

        serializer = NoteSerializer(note)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_note_update(self):
        note = NoteFactory(creator=self.user)
        CourseRelation.objects.create(course=note.course, creator=self.user)

        payload = {
            'time': '12:30:00'
        }
        response = self.client.patch(note_detail_url(pk=note.id), payload)

        note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(datetime.strptime(payload['time'], '%H:%M:%S').time(), note.time)

    def test_full_note_update(self):
        note = NoteFactory(creator=self.user)
        CourseRelation.objects.create(course=note.course, creator=self.user)

        payload = {
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.put(note_detail_url(note.id), payload)

        note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(note.note, payload['note'])
        self.assertEqual(datetime.strptime(payload['time'], '%H:%M:%S').time(), note.time)

    def test_delete_note(self):
        note = NoteFactory(creator=self.user)
        CourseRelation.objects.create(course=note.course, creator=self.user)

        response = self.client.delete(note_detail_url(pk=note.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(id=note.id).exists())
