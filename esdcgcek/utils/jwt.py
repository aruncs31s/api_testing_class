import requests

from esdcgcek.apis.base import SERVER_URL
from esdcgcek.auth.apis import LOGIN

LOGIN_URL = SERVER_URL + LOGIN

def get_jwt(
        email: str,
        password: str
) -> str:
    return requests.post(LOGIN_URL, json={"email": email, "password": password}).json()["token"]

def main()-> str:
    return get_jwt("ganga@gamil.com", "gangav")

def get_gangas_token()-> str:
    return main()