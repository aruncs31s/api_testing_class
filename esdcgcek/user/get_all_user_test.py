from esdcgcek.utils.jwt import get_gangas_token

import requests
# from esdcgcek.apis.base import SERVER_URL
# from esdcgcek.user.apis import USER

SERVER_URL = "https://api.esdcgcek.in/api/users"
def test_get_all_users():
    token = get_gangas_token()
    print(token)
    # headers = {"Authorization": f"Bearer {token}"}
    headers = {
        'Authorization': f"Bearer {token}"
        }
    response = requests.get(SERVER_URL, headers=headers)
    # assert response.status_code == 200
    print(response.json())