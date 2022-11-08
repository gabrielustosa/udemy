from django.urls import path

from . import views
from udemy.apps.action import views as action_views

app_name = 'rating'

urlpatterns = [
    path('', views.RatingViewSet.as_view({'post': 'create'}), name='list'),
    path(
        '<int:id>/',
        views.RatingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}),
        name='detail'
    ),
    path(
        '<int:rating_id>/action/',
        action_views.RatingActionViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}),
        name='action-list'
    ),
    path(
        '<int:rating_id>/action/<int:action>/',
        action_views.RatingActionViewSet.as_view({'get': 'retrieve'}),
        name='action-detail'
    ),
]
