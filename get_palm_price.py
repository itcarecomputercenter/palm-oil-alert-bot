import requests
import datetime
import os
import re
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_usd_price():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    try:
        price_span = soup.find('span', class_='price-section__current-value')
        if price_span:
            return f"{price_span.text.strip()} USD/ton"
    except Exception as e:
        return f"Error fetching USD price: {e}"
    return "USD Price not found."

def get_myr_price():
    url = "https://tradingeconomics.com/commodity/palm-oil"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    try:
        match = re.search(r'"Last":([\d.]+),', res.text)
        if match:
            return f"{match.group(1)} MYR/ton"
    except Exception as e:
        return f"Error fetching MYR price: {e}"
    return "MYR Price not found."

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    usd = get_usd_price()
    myr = get_myr_price()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    message = f"🛢️ Palm Oil Price Update ({now}):\nUSD Price: {usd}\nMYR Price: {myr}"
    send_telegram_message(message)
