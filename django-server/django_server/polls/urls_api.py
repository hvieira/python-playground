from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path('', views.QuestionListApiView.as_view()),
]