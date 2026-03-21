import requests

url = "https://api.esdcgcek.in/api/users/search?query=gan"

payload = {}
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzQzNjYzNzEsInJvbGUiOiJ0ZWFjaGVyIiwidXNlcl9pZCI6ImIyOWQxMjcxLWVlNDQtNDNmNS1hZmFhLWViNjk1ZTkxZmUxZiJ9.SWOJtDZq2Sc0bxDiEFRI7-erWK1pRl0_sdfmifN5rYQ",
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
