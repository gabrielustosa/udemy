from django.urls import path

from . import views
from udemy.apps.action import views as action_views

app_name = 'question'

urlpatterns = [
    path('', views.QuestionViewSet.as_view({'post': 'create'}), name='list'),
    path(
        '<int:id>/',
        views.QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}),
        name='detail'
    ),
    path(
        '<int:question_id>/action/',
        action_views.QuestionActionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='action-list'
    ),
    path(
        '<int:question_id>/action/<int:action>/',
        action_views.QuestionActionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='action-detail'
    ),
]
