from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('', views.ContentViewSet, basename='content')

urlpatterns = router.urls
