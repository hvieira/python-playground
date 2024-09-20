from typing import Generator
import pytest  
  
from rest_framework.test import RequestsClient
  
  
@pytest.fixture()  
def api_client() -> Generator[RequestsClient, None, None]:  
    """  
    Fixture to provide an API client  
    :return: APIClient  
    """  
    yield RequestsClient()
