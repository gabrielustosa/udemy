from datetime import datetime

from django.test import TestCase

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.note import NoteFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.note.models import Note
from udemy.apps.question.models import Answer

NOTE_LIST_URL = reverse('note-list')


def note_detail_url(pk): return reverse('note-detail', kwargs={'pk': pk})


class PublicNoteAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_note(self):
        response = self.client.post(NOTE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAnswerAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_note(self):
        course = CourseFactory()
        LessonFactory(course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'lesson': 1,
            'course': 1,
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.post(NOTE_LIST_URL, payload)

        note = Note.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(datetime.strptime(payload['time'], '%H:%M:%S').time(), note.time)
        self.assertEqual(payload['note'], note.note)

    def test_partial_note_update(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        note = NoteFactory(creator=self.user, lesson=lesson, course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'time': '12:30:00'
        }
        response = self.client.patch(note_detail_url(pk=note.id), payload)

        note.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(datetime.strptime(payload['time'], '%H:%M:%S').time(), note.time)

    def test_delete_answer(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        note = NoteFactory(creator=self.user, lesson=lesson, course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        response = self.client.delete(note_detail_url(pk=note.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Answer.objects.filter(id=note.id).exists())

    def test_not_creator_note_can_update_note(self):
        user = UserFactory()
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        note = NoteFactory(creator=user, lesson=lesson, course=course)
        CourseRelation.objects.create(course=course, creator=user)

        payload = {
            'time': '12:30:00'
        }
        response = self.client.patch(note_detail_url(pk=note.id), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_enrolled_can_create_course(self):
        course = CourseFactory()
        LessonFactory(course=course)

        payload = {
            'lesson': 1,
            'course': 1,
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.post(NOTE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
