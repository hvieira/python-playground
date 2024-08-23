from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# to avoid the warning, use from .models import Question
from polls.models import Question
from polls.serializers import QuestionSerializer


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)



class QuestionListApiView(APIView):
    
    def get(self, request, *args, **kwargs):
        '''
        List all questions
        '''
        todos = Question.objects.all()
        serializer = QuestionSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)