from typing import Generator
import pytest  
  
from rest_framework.test import RequestsClient
  
from store_api.models import User

  
@pytest.fixture()
def api_client() -> Generator[RequestsClient, None, None]:  
    """  
    Fixture to provide an API client  
    :return: RequestsClient  
    """  
    yield RequestsClient()


@pytest.fixture()
def default_password() -> str:
    return 'l33t!passwdzzz'


@pytest.fixture()
def default_user(default_password: str) -> Generator[User, None, None]:
    yield User.objects.create_user(
        email='john.doe@test.com',
        username='john.doe',
        password=default_password
    )
