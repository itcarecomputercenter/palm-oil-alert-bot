import requests
import json
import os
from datetime import datetime
import time

# === Config ===
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # or channel username with @
YESTERDAY_FILE = "yesterday_data.json"

# === Palm Oil Data Source ===
def get_palm_price_usd():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch palm oil price page")

    import re
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    match = re.search(r"Palm Oil \((.*?)\)\s+Price\s+\$([\d,.]+)", soup.text)
    if not match:
        raise Exception("Palm oil price not found")
    return float(match.group(2).replace(",", ""))  # USD/ton

# === Currency Conversion ===
def get_usd_to_php():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=PHP"
    r = requests.get(url)
    return r.json()["rates"]["PHP"]

# === Telegram Notification ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# === File Save/Load ===
def load_yesterday_data():
    if not os.path.exists(YESTERDAY_FILE):
        return None
    try:
        with open(YESTERDAY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except json.JSONDecodeError:
        return None

def save_today_data(usd_price, usd_to_php):
    with open(YESTERDAY_FILE, "w") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "usd_price": usd_price,
            "usd_to_php": usd_to_php
        }, f)

# === Change Analyzer ===
def generate_price_summary(today_price_usd, today_php, yesterday_data):
    if not yesterday_data:
        return (
            f"🌴 <b>Palm Oil Price Update</b> ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            f"• Price: <b>${today_price_usd:.2f}</b> / ton\n"
            f"• USD to PHP: <b>{today_php:.2f}</b>\n"
            f"• Peso Price: <b>₱{today_price_usd * today_php:,.2f}</b> / ton\n\n"
            "📌 No data for yesterday. First time update."
        )

    y_usd = yesterday_data["usd_price"]
    y_php = yesterday_data["usd_to_php"]
    y_peso = y_usd * y_php
    t_peso = today_price_usd * today_php

    usd_diff = today_price_usd - y_usd
    usd_pct = (usd_diff / y_usd) * 100 if y_usd else 0

    php_diff = today_php - y_php
    php_pct = (php_diff / y_php) * 100 if y_php else 0

    peso_diff = t_peso - y_peso
    peso_pct = (peso_diff / y_peso) * 100 if y_peso else 0

    cause = []
    if abs(usd_pct) > 0.5:
        cause.append("Palm Oil Price")
    if abs(php_pct) > 0.5:
        cause.append("Exchange Rate")

    return (
        f"🌴 <b>Palm Oil Price Update</b> ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        f"• Price: <b>${today_price_usd:.2f}</b> ({usd_pct:+.2f}%)\n"
        f"• USD to PHP: <b>{today_php:.2f}</b> ({php_pct:+.2f}%)\n"
        f"• Peso Price: <b>₱{t_peso:,.2f}</b> ({peso_pct:+.2f}%)\n\n"
        f"📈 Change likely due to: <b>{', '.join(cause) if cause else 'No major change'}</b>"
    )

# === Main ===
if __name__ == "__main__":
    try:
        usd_price = get_palm_price_usd()
        usd_to_php = get_usd_to_php()
        yesterday_data = load_yesterday_data()
        summary = generate_price_summary(usd_price, usd_to_php, yesterday_data)
        print(summary)
        send_telegram_message(summary)
        save_today_data(usd_price, usd_to_php)
    except Exception as e:
        send_telegram_message(f"⚠️ Palm Oil Bot Error:\n{str(e)}")
        raise
