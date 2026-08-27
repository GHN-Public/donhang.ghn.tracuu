import requests
from config import BOT_TOKEN, CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text):
    url = f"{BASE_URL}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print(response.status_code)
    print(response.text)