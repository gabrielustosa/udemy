from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('', views.RatingViewSet, basename='rating')

urlpatterns = router.urls
