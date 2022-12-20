from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.course.models import Course
from udemy.apps.user.serializer import UserSerializer


class CourseSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline', 'language', 'description',
            'is_paid', 'price', 'created', 'modified',
            'requirements', 'what_you_will_learn',
            'categories', 'instructors', 'url',
        ]
        extra_kwargs = {
            'instructors': {'allow_empty': True},
        }
        related_objects = {
            'instructors': {
                'serializer': UserSerializer,
                'many': True,
            },
            'categories': {
                'serializer': CategorySerializer,
                'many': True,
            },
            'quizzes': {
                'serializer': 'udemy.apps.quiz.serializer.QuizSerializer',
                'permissions': [IsEnrolled],
                'filter': {'is_published': True},
                'many': True,
            },
            'lessons': {
                'serializer': 'udemy.apps.lesson.serializer.LessonSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'modules': {
                'serializer': 'udemy.apps.module.serializer.ModuleSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'contents': {
                'serializer': 'udemy.apps.content.serializer.ContentSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'ratings': {
                'serializer': 'udemy.apps.rating.serializer.RatingSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'warning_messages': {
                'serializer': 'udemy.apps.message.serializer.MessageSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'questions': {
                'serializer': 'udemy.apps.question.serializer.QuestionSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'notes': {
                'serializer': 'udemy.apps.note.serializer.NoteSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            },
            'lesson_relations': {
                'serializer': 'udemy.apps.lesson.serializer.LessonRelationSerializer',
                'permissions': [IsEnrolled],
                'many': True,
            }
        }
        min_fields = ('id', 'title', 'url')
        default_fields = (*min_fields, 'price', 'is_paid', 'instructors')

    def get_url(self, instance):
        return f'https://udemy.com/course/{instance.slug}'

    def get_related_objects(self):
        related_objects = super().get_related_objects()
        user = getattr(self.context.get('request'), 'user', None)
        if user:
            related_objects['notes']['filter'] = {
                'creator': user
            }
            related_objects['lesson_relations']['filter'] = {
                'creator': user
            }
        return related_objects

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course
