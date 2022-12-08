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
            'is_paid', 'price', 'created', 'modified', 'avg_rating',
            'requirements', 'what_you_will_learn', 'num_contents_info',
            'categories', 'instructors', 'num_modules', 'url', 'num_subscribers',
            'num_lessons', 'num_contents', 'estimated_content_length_video'
        ]
        extra_kwargs = {
            'instructors': {'allow_empty': True},
        }
        related_objects = {
            'instructors': {
                'serializer': UserSerializer
            },
            'categories': {
                'serializer': CategorySerializer,
            },
            'quizzes': {
                'serializer': 'udemy.apps.quiz.serializer.QuizSerializer',
                'permissions': [IsAuthenticated, IsEnrolled],
                'filter': {'is_published': True},
            },
            'lessons': {
                'serializer': 'udemy.apps.lesson.serializer.LessonSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'modules': {
                'serializer': 'udemy.apps.module.serializer.ModuleSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'contents': {
                'serializer': 'udemy.apps.content.serializer.ContentSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'ratings': {
                'serializer': 'udemy.apps.rating.serializer.RatingSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'warning_messages': {
                'serializer': 'udemy.apps.message.serializer.MessageSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'questions': {
                'serializer': 'udemy.apps.question.serializer.QuestionSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'notes': {
                'serializer': 'udemy.apps.note.serializer.NoteSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            },
            'lesson_relations': {
                'serializer': 'udemy.apps.lesson.serializer.LessonRelationSerializer',
                'permissions': [IsAuthenticated, IsEnrolled]
            }
        }
        min_fields = ('id', 'title', 'url')
        default_fields = (*min_fields, 'price', 'is_paid', 'instructors')

    def get_url(self, instance):
        return f'https://udemy.com/course/{instance.slug}'

    def get_related_objects(self):
        related_objects = super().get_related_objects()
        if self.context.get('request'):
            related_objects['notes']['filter'] = {
                'creator': self.context.get('request').user
            }
            related_objects['lesson_relations']['filter'] = {
                'creator': self.context.get('request').user
            }
        return related_objects

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course
