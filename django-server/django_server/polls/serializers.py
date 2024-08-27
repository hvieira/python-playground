from rest_framework import serializers
from .models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', "question_text", "pub_date", 'choices']
        depth = 1

    choices = ChoiceSerializer(required=False, many=True, source='choice_set')


