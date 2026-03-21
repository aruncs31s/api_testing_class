from dataclasses import asdict, dataclass
import json
import requests

from apis import SERVER_URL, LOGIN

url = SERVER_URL + LOGIN


def register_user():
    email = "ganga@gamil.com"
    password = "gangav"

    response = requests.post(url, json={"email": email, "password": password})
    print(response.status_code)

    json_data = response.json()
    return json_data
def test_register_user():
    response = register_user()
    assert "user"  in response
    assert "token" in response

def test_register_user_role():
    response =register_user()
    user = response["user"]
    assert "role" in user