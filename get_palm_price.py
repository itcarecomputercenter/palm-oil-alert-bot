import requests
import datetime
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_palm_oil_price():
    url = "https://www.investing.com/commodities/palm-oil"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    text = response.text

    # Look for known text pattern (works as of July 2025)
    try:
        start = text.index('"last_last":') + len('"last_last":')
        end = text.index(',', start)
        price = text[start:end]
        return f"{price} USD/ton"
    except ValueError:
        return "Price not found."

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    price = get_palm_oil_price()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    message = f"🛢️ Palm Oil Price Update ({now}):\nCurrent Price: {price}"
    send_telegram_message(message)
