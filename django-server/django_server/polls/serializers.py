from rest_framework import serializers
from .models import Choice, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', "question_text", "pub_date", 'choice_set']
        depth = 1
        


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']
