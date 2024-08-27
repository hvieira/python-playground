from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path('', views.QuestionListAPIView.as_view()),
    path('<int:pk>/', views.QuestionDetailAPIView.as_view()),
    path('<int:pk>/choices', views.QuestionChoicesAPIView.as_view()),
]