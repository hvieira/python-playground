from rest_framework.routers import SimpleRouter

from store_api import views

router = SimpleRouter(use_regex_path=False)
router.register(r"", views.UserViewSet)

urlpatterns = router.urls
