import requests
import datetime
import os
import json
from bs4 import BeautifulSoup

# === CONFIG ===
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
HISTORY_FILE = "palm_price_history.json"

# Cost assumptions (in PHP)
freight = 2.5
refining = 2.5
tax = 1.5
logistics = 2.0
markup = 5.0
buffer = 1.0

def get_usd_php_rate():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=PHP"
    try:
        res = requests.get(url)
        rate = res.json()['rates']['PHP']
        return round(rate, 2)
    except Exception:
        return 58.0  # fallback

def get_usd_price():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_span = soup.find('span', class_='price-section__current-value')
        if price_span:
            return float(price_span.text.replace(',', '').strip())
    except:
        return None

def calculate_php_price(usd_price, exchange_rate):
    base_php_per_kg = round((usd_price * exchange_rate) / 1000, 2)
    retail_php_per_kg = round(base_php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
    return base_php_per_kg, retail_php_per_kg

def load_yesterday_data():
    if os.path.exists(HISTORY_FILE):
        return None
        
        with open(HISTORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return None
            try:
                yesterday_data = load_yesterday_data()
            except Exception as e:
                print("⚠️ Failed to load yesterday's data:", str(e))
                yesterday_data = None
            return json.load(f)
    return None

def save_today_data(today_data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(today_data, f)

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})

def compare_and_report(today, yesterday):
    change_usd = today["usd_price"] - yesterday["usd_price"]
    change_fx = today["usd_php"] - yesterday["usd_php"]
    change_php_kg = today["base_php"] - yesterday["base_php"]

    pct_usd = round((change_usd / yesterday["usd_price"]) * 100, 2)
    pct_fx = round((change_fx / yesterday["usd_php"]) * 100, 2)
    pct_php = round((change_php_kg / yesterday["base_php"]) * 100, 2)

    reason = "🛢️ Palm oil price" if abs(pct_usd) > abs(pct_fx) else "💱 USD/PHP rate"

    return (
        f"🛢️ Palm Oil Price Update ({today['timestamp']}):\n\n"
        f"🌐 Palm Oil: {today['usd_price']} USD/ton ({'+' if change_usd >= 0 else ''}{pct_usd}%)\n"
        f"💱 USD to PHP: {today['usd_php']} ({'+' if change_fx >= 0 else ''}{pct_fx}%)\n"
        f"→ Base: ₱{today['base_php']}/kg ({'+' if change_php_kg >= 0 else ''}{pct_php}%)\n"
        f"→ Est. Retail: ₱{today['retail_php']}/kg\n\n"
        f"📌 Main driver: {reason}"
    )

if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    usd_price = get_usd_price()
    usd_php = get_usd_php_rate()

    if usd_price is None:
        send_telegram_message(f"❌ Unable to fetch palm oil price for {now}.")
        exit()

    base_php, retail_php = calculate_php_price(usd_price, usd_php)

    today_data = {
        "timestamp": now,
        "usd_price": usd_price,
        "usd_php": usd_php,
        "base_php": base_php,
        "retail_php": retail_php
    }

    yesterday_data = load_yesterday_data()

    if yesterday_data:
        msg = compare_and_report(today_data, yesterday_data)
    else:
        msg = (
            f"🛢️ Palm Oil Price Update ({now}):\n\n"
            f"🌐 Palm Oil: {usd_price} USD/ton\n"
            f"💱 USD to PHP: {usd_php}\n"
            f"→ Base: ₱{base_php}/kg\n"
            f"→ Est. Retail: ₱{retail_php}/kg\n\n"
            f"📌 No comparison (first run)"
        )

    save_today_data(today_data)
    send_telegram_message(msg)
