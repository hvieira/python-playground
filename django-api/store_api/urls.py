from rest_framework.routers import SimpleRouter

from store_api import views

router = SimpleRouter(use_regex_path=False)
router.register(r"users", views.UserViewSet)
router.register(r"products", views.ProductViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"orders", views.OrderViewSet)

urlpatterns = router.urls
