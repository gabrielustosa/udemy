from django.urls import path

from . import views

app_name = 'action'

urlpatterns = [
    path('', views.ActionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'post': 'create'}), name='list')
]
