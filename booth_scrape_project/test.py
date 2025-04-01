import requests

API_SERVER_URL = "http://localhost:11434/api/chat"


def main():
    headers = {"Content-Type": "application/json"}
    json = {
        "model": "deepseek-r1:14b",
        "messages": [{
            "role": "user",
            "content": "Hello",
        }]
    }

    response = requests.post(API_SERVER_URL, headers=headers, json=json)
    response.raise_for_status()

    print(response.text)

main()