from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # TODO the name should not clash with other app's urls - "index" is quite common
    # https://docs.djangoproject.com/en/5.1/topics/http/urls/#naming-url-patterns
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),

    path('api', views.QuestionListApiView.as_view()),
]