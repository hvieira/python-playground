from django.urls import path

from . import views

urlpatterns = [
    # TODO the name should not clash with other app's urls - "index" is quite common
    # https://docs.djangoproject.com/en/5.1/topics/http/urls/#naming-url-patterns
    path("", views.index, name="index"),
]