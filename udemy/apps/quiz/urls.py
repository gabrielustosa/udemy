from django.urls import path, include

from rest_framework.routers import SimpleRouter

from . import views

app_name = 'quiz'

router_quiz = SimpleRouter()
router_quiz.register(r'quiz', views.QuizViewSet, basename='quiz')

router_question = SimpleRouter()
router_question.register(r'question', views.QuestionViewSet, basename='quiz-question')

urlpatterns = [
    path('', include(router_quiz.urls)),
    path('quiz/<int:quiz_id>/', include(router_question.urls)),
    path('quiz/<int:quiz_id>/check/', views.CheckQuizView.as_view(), name='check'),
]
