import json
import requests

from apis import SERVER_URL, LOGIN
SERVER_URL="https://api.esdcgcek.in"
url = SERVER_URL + LOGIN

EMAIL = "ganga@gamil.com"
PASSWORD = "gangav"

def test_login():
    response = requests.post(url, json={"email": EMAIL, "password": PASSWORD})
    print(response.status_code)