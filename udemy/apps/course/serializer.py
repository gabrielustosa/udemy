from django.db.models import Sum, Count, Q, Avg

from rest_framework import serializers

from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.course.models import Course
from udemy.apps.user.serializer import UserSerializer


class CourseSerializer(ModelSerializer):
    num_modules = serializers.SerializerMethodField()
    num_lessons = serializers.SerializerMethodField()
    num_contents = serializers.SerializerMethodField()
    num_contents_info = serializers.SerializerMethodField()
    num_subscribers = serializers.SerializerMethodField()
    estimated_content_length_video = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
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
            'instructors': {'required': False},
            'categories': {'required': False},
        }
        related_objects = {
            'instructors': UserSerializer,
            'categories': CategorySerializer,
            'quizzes': 'udemy.apps.quiz.serializer.QuizSerializer',
            'lessons': 'udemy.apps.lesson.serializer.LessonSerializer',
            'modules': 'udemy.apps.module.serializer.ModuleSerializer',
            'contents': 'udemy.apps.content.serializer.ContentSerializer',
            'ratings': 'udemy.apps.rating.serializer.RatingSerializer',
            'warning_messages': 'udemy.apps.message.serializer.MessageSerializer',
            'questions': 'udemy.apps.question.serializer.QuestionSerializer',
            'notes': 'udemy.apps.note.serializer.NoteSerializer'
        }
        related_objects_permissions = {
            ('quizzes', 'lessons', 'notes',
             'modules', 'contents', 'questions',
             'warning_messages',): [IsEnrolled]
        }
        related_objects_filters = {
            'quizzes': {'is_published': True}
        }
        min_fields = ('id', 'title', 'url')
        default_fields = (*min_fields, 'price', 'is_paid', 'instructors')

    def get_num_modules(self, instance):
        return instance.modules.count()

    def get_num_lessons(self, instance):
        return instance.lessons.count()

    def get_num_contents(self, instance):
        return instance.contents.count()

    def get_avg_rating(self, instance: Course):
        return instance.ratings.aggregate(avg=Avg('rating'))['avg']

    def get_url(self, instance):
        return f'https://udemy.com/course/{instance.slug}'

    def get_num_subscribers(self, instance):
        return instance.students.count()

    def get_num_contents_info(self, instance):
        return instance.contents.aggregate(
            **{option: Count('id', filter=Q(content_type__model=option))
               for option in ['text', 'link', 'file', 'image']},
        )

    def get_estimated_content_length_video(self, instance: Course):
        return instance.lessons.aggregate(length_video=Sum('video_duration'))['length_video']

    def get_related_objects_filters(self):
        related_objects_filters = super().get_related_objects_filters()
        related_objects_filters['notes'] = {
            'creator': self.context.get('request').user
        }
        return related_objects_filters

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course


