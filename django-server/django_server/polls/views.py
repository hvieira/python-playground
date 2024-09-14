from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Question
from .serializers import ChoiceSerializer, QuestionSerializer


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



class QuestionListAPIView(APIView):
    
    def get(self, _request: Request):
        '''
        List all questions
        '''
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    def post(self, request: Request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailAPIView(APIView):
    
    def get(self, _request: Request, pk=None):
        '''
        Get Question detail
        '''
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    # TODO missing update on PUT for question
    # TODO missing DELETE on PUT for question


class QuestionChoicesAPIView(APIView):
    
    def get(self, _request: Request, pk=None):
        '''
        List all choices for a question
        '''
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChoiceSerializer(question.choice_set, many=True)
        return Response(serializer.data)


class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
