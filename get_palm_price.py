import requests
from bs4 import BeautifulSoup
import datetime
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_palm_oil_price():
    url = 'https://tradingeconomics.com/commodity/palm-oil'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_box = soup.find('td', {'class': 'datatable-item last'})
    return price_box.text.strip() if price_box else 'Price not found.'

def send_telegram_message(msg):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    price = get_palm_oil_price()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    message = f'🛢️ Palm Oil Price Update ({now}):\nCurrent Price: {price}'
    send_telegram_message(message)
