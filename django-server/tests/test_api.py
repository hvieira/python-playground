import pytest

from django.utils import timezone
from rest_framework.test import APIClient

from polls.models import Question


@pytest.mark.django_db
def test_get_polls_nothing_in_db(api_client: APIClient):
    response = api_client.get('/api/polls/')
    assert response.data == []


@pytest.mark.django_db
def test_get_polls_with_existing_polls(api_client: APIClient):
    q1 = Question(question_text='Thoughts about Django?', pub_date=timezone.now())
    q2 = Question(question_text='What about X?', pub_date=timezone.now())

    q1.save()
    q2.save()

    q2.choice_set.create(choice_text='Really bad')
    q2.choice_set.create(choice_text='Meh')
    q2.choice_set.create(choice_text='Good enough')

    response = api_client.get('/api/polls/')
    
    # TODO datetime objects do not support Z (Zulu time suffix) or any other military suffixes
    # one solution would be to use explicit time zone - e.g. "+00:00", in this case. This would need a change in the serializers
    assert response.data == [
        {
            'id': 1,
            'question_text': q1.question_text,
            'pub_date': q1.pub_date.isoformat().replace('+00:00', 'Z'),
            'choices': []

        },
        {
            'id': 2,
            'question_text': q2.question_text,
            'pub_date': q2.pub_date.isoformat().replace('+00:00', 'Z'),
            'choices': [
                {
                    'id': 1, 
                    'choice_text': 'Really bad',
                    'votes': 0
                },                
                {
                    'id': 2, 
                    'choice_text': 'Meh',
                    'votes': 0
                },                
                {
                    'id': 3, 
                    'choice_text': 'Good enough',
                    'votes': 0
                },
            ]
        }
    ]
