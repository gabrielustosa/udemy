from django.urls import path

from . import views
from udemy.apps.action import views as action_views
from udemy.apps.answer import views as answer_views

app_name = 'question'

urlpatterns = [
    path('', views.QuestionViewSet.as_view({'post': 'create'}), name='list'),
    path(
        '<int:pk>/',
        views.QuestionViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='detail'
    ),
    path(
        '<int:question_id>/action/',
        action_views.QuestionActionViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='action-list'
    ),
    path(
        '<int:question_id>/action/<int:action>/',
        action_views.QuestionActionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='action-detail'
    ),
    path(
        '<int:question_id>/answer/',
        answer_views.QuestionAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answer-list'
    ),
]
