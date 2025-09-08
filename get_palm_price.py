import requests
import datetime
import os
from bs4 import BeautifulSoup

# === CONFIG ===
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

# Exchange rate
usd_to_php = 58.0  # USD to PHP conversion rate

# Add-on cost estimates (in PHP per kg)
freight = 2.5
refining = 2.5
tax = 1.5
logistics = 2.0
markup = 5.0
buffer = 1.0

def get_usd_price():
    url = "https://ph.investing.com/commodities/rbd-palm-olein"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        price_span = soup.find('span', class_='price-section__current-value')
        if price_span:
            price_usd = float(price_span.text.replace(',', '').strip())
            php_per_kg = round((price_usd * usd_to_php) / 1000, 2)
            retail_est = round(php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
            return price_usd, php_per_kg, retail_est
        else:
            return None, None, "❌ USD price not found on page."
    except Exception as e:
        return None, None, f"❌ Error fetching USD price: {e}"

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': msg
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    usd_price, usd_php_kg, usd_final = get_usd_price()

    if isinstance(usd_final, str):
        # If error message returned
        message = (
            f"🛢️ Palm Oil Price Update ({now}):\n\n"
            f"{usd_final}\n\n"
            f"⚠️ USD fallback failed. Please check manually."
        )
    else:
        message = (
            f"🛢️ Palm Oil Price Update ({now}):\n\n"
            f"🌐 USD Price: {usd_price} USD/ton\n"
            f"→ Base: ₱{usd_php_kg}/kg\n"
            f"→ Est. Retail: ₱{usd_final}/kg\n\n"
            f"⚠️ MYR price currently unavailable. Showing USD estimate only."
        )

    send_telegram_message(message)
