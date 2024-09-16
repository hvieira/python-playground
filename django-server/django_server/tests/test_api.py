import pytest

from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient


class APITests(TestCase):
    
    def test_dummy(self):
        assert True == True

# @pytest.mark.django_db
# def test_create_task(api_client) -> None:
#     assert True == True