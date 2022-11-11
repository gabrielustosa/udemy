from django.urls import path

from . import views
from udemy.apps.action import views as action_views
from udemy.apps.answer import views as answer_views

app_name = 'rating'

urlpatterns = [
    path('', views.RatingViewSet.as_view({'post': 'create', 'get': 'list'}), name='list'),
    path(
        '<int:pk>/',
        views.RatingViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='detail'
    ),
    path(
        '<int:rating_id>/action/',
        action_views.RatingActionViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='action-list'
    ),
    path(
        '<int:rating_id>/action/<int:action>/',
        action_views.RatingActionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='action-detail'
    ),
    path(
        '<int:rating_id>/answer/',
        answer_views.RatingAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answer-list'
    ),
]
