# palm_oil_bot/get_palm_price.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import telegram

# === CONFIG ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USD_TO_PHP_API = "https://api.exchangerate.host/latest?base=USD&symbols=PHP"
YESTERDAY_FILE = "yesterday_data.json"

def fetch_usd_palm_price():
    try:
        r = requests.get("https://markets.businessinsider.com/commodities/palm-oil-price")
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.select_one(".price-section__current-value")
        return float(el.text.replace(",", "")) if el else None
    except:
        return None

def fetch_myr_palm_price():
    try:
        r = requests.get("https://tradingeconomics.com/commodity/palm-oil")
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.select_one(".table-hover .datatable-row:nth-of-type(1) td:nth-of-type(2)")
        return float(el.text.replace(",", "")) if el else None
    except:
        return None

def fetch_usd_to_php():
    try:
        r = requests.get(USD_TO_PHP_API)
        return r.json()["rates"]["PHP"]
    except:
        return None

def load_yesterday_data():
    if not os.path.exists(YESTERDAY_FILE):
        return None
    with open(YESTERDAY_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

def save_today_data(data):
    with open(YESTERDAY_FILE, "w") as f:
        json.dump(data, f)

def format_change(current, previous):
    if previous is None or current is None:
        return "N/A"
    diff = current - previous
    pct = (diff / previous) * 100 if previous else 0
    symbol = "⬆" if diff > 0 else ("⬇" if diff < 0 else "➡")
    return f"{symbol} {diff:.2f} ({pct:+.2f}%)"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    usd_price = fetch_usd_palm_price()
    myr_price = fetch_myr_palm_price()
    usd_to_php = fetch_usd_to_php()

    yesterday_data = load_yesterday_data()

    usd_change = format_change(usd_price, yesterday_data.get("usd_price") if yesterday_data else None)
    fx_change = format_change(usd_to_php, yesterday_data.get("usd_to_php") if yesterday_data else None)

    price_in_php = usd_price * usd_to_php if usd_price and usd_to_php else None

    msg = f"\ud83d\udcc8 Palm Oil Price Update ({now}):\n\n"
    msg += f"USD Price: {usd_price:.2f} USD/MT {f'({usd_change})' if usd_change else ''}\n" if usd_price else "USD price not found.\n"
    msg += f"MYR Price: {myr_price:.2f} MYR/MT\n" if myr_price else "\u274c MYR price not found.\n"
    msg += f"USD to PHP: {usd_to_php:.2f} {f'({fx_change})' if fx_change else ''}\n" if usd_to_php else "\u274c USD to PHP not found.\n"
    msg += f"\n\ud83d\udcb5 Estimated Price in PHP: {price_in_php:.2f} PHP/MT\n" if price_in_php else ""
    msg += f"\ud83d\udcca PHP/KG: {price_in_php / 1000:.2f} PHP/kg\n" if price_in_php else ""

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

    # Save today's data
    save_today_data({
        "usd_price": usd_price,
        "myr_price": myr_price,
        "usd_to_php": usd_to_php
    })

if __name__ == "__main__":
    main()
