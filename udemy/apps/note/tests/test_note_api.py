from datetime import datetime

from django.test import TestCase
from parameterized import parameterized

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.note import NoteFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.note.models import Note
from udemy.apps.note.serializer import NoteSerializer
from udemy.apps.user.serializer import UserSerializer

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
        lesson = LessonFactory(course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'lesson': lesson.id,
            'course': course.id,
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

    def test_full_note_update(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        note = NoteFactory(creator=self.user, lesson=lesson, course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

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
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        note = NoteFactory(creator=self.user, lesson=lesson, course=course)
        CourseRelation.objects.create(course=course, creator=self.user)

        response = self.client.delete(note_detail_url(pk=note.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(id=note.id).exists())

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
        lesson = LessonFactory(course=course)

        payload = {
            'lesson': lesson.id,
            'course': course.id,
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.post(NOTE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        ('lesson', ('id', 'title'), LessonSerializer),
        ('creator', ('id', 'name'), UserSerializer),
        ('course', ('id', 'title'), CourseSerializer),
    ])
    def test_related_objects(self, field_name, fields, Serializer):
        note = NoteFactory(creator=self.user)
        CourseRelation.objects.create(course=note.course, creator=self.user)

        response = self.client.get(
            f'{note_detail_url(note.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        note_serializer = NoteSerializer(note, fields=('@min',))
        object_serializer = Serializer(getattr(note, field_name), fields=fields)

        expected_response = {
            **note_serializer.data,
            field_name: {
                **object_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_permission_for_field(self):
        course = CourseFactory()
        lesson = LessonFactory()
        CourseRelation.objects.create(course=course, creator=self.user)

        payload = {
            'lesson': lesson.id,
            'course': course.id,
            'note': 'Note',
            'time': '12:34:56',
        }
        response = self.client.post(NOTE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
