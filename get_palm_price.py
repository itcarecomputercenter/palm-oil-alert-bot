import requests
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # or @channelusername

# === Fetch Palm Oil Price in USD ===
def get_palm_price_usd():
    url = "https://markets.businessinsider.com/commodities/palm-oil-price"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to fetch palm oil price page")

    from bs4 import BeautifulSoup
    import re
    soup = BeautifulSoup(r.text, "html.parser")
    match = re.search(r"Palm Oil \((.*?)\)\s+Price\s+\$([\d,.]+)", soup.text)
    if not match:
        raise Exception("Palm oil price not found")
    return float(match.group(2).replace(",", ""))

# === Fetch USD to PHP Conversion Rate ===
def get_usd_to_php():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=PHP"
    r = requests.get(url)
    return r.json()["rates"]["PHP"]

# === Send Telegram Alert ===
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# === Main Logic ===
if __name__ == "__main__":
    try:
        usd_price = get_palm_price_usd()
        usd_to_php = get_usd_to_php()
        peso_price = usd_price * usd_to_php

        message = (
            f"🌴 <b>Palm Oil Daily Price</b>\n"
            f"📅 <b>{datetime.now().strftime('%Y-%m-%d')}</b>\n\n"
            f"• USD Price: <b>${usd_price:.2f}</b> / ton\n"
            f"• USD to PHP: <b>{usd_to_php:.2f}</b>\n"
            f"• Price in PHP: <b>₱{peso_price:,.2f}</b> / ton"
        )

        send_telegram_message(message)
        print("✅ Message sent successfully.")
    except Exception as e:
        send_telegram_message(f"⚠️ Error in Palm Oil Bot:\n{str(e)}")
        raise
