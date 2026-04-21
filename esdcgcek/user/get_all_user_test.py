from esdcgcek.utils.jwt import get_gangas_token
import pytest
import requests
from esdcgcek.apis.base import SERVER_URL
from esdcgcek.user.apis import USER


USER_URL = SERVER_URL + USER


@pytest.fixture(scope="module")
def get_header():
    return {"Authorization": f"Bearer {get_gangas_token()}"}


def test_get_all_users(get_header):
    headers = get_header
    response = requests.get(USER_URL, headers=headers)
    
