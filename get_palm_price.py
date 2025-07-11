import requests
import datetime
import os
import re
from bs4 import BeautifulSoup

# === CONFIG ===
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

usd_to_php = 58.0  # update as needed
myr_to_php = 12.5  # update as needed

# Estimated cost breakdown (in PHP/kg)
freight = 2.5
refining = 2.5
tax = 1.5
logistics = 2.0
markup = 5.0
buffer = 1.0

def get_usd_price():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    try:
        price_span = soup.find('span', class_='price-section__current-value')
        if price_span:
            price_usd = float(price_span.text.replace(',', '').strip())
            php_per_kg = round((price_usd * usd_to_php) / 1000, 2)
            local_estimate = round(php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
            return price_usd, php_per_kg, local_estimate
    except Exception as e:
        return None, None, f"Error fetching USD price: {e}"
    return None, None, "USD Price not found"

def get_myr_price():
    url = "https://tradingeconomics.com/commodity/palm-oil"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    try:
        match = re.search(r'"Last":([\d.]+),', res.text)
        if match:
            price_myr = float(match.group(1))
            php_per_kg = round((price_myr * myr_to_php) / 1000, 2)
            local_estimate = round(php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
            return price_myr, php_per_kg, local_estimate
    except Exception as e:
        return None, None, f"Error fetching MYR price: {e}"
    return None, None, "MYR Price not found"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main
