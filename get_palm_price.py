import requests
import datetime
import os
import re
from bs4 import BeautifulSoup

# === CONFIG ===
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

# Exchange rates
usd_to_php = 58.0  # adjust as needed
myr_to_php = 12.5  # adjust as needed

# Add-on costs per kg
freight = 2.5      # import/shipping
refining = 2.5     # processing
tax = 1.5          # VAT/duty
logistics = 2.0    # local delivery
markup = 5.0       # reseller margin
buffer = 1.0       # packaging/hedging

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
        return None, None, f"❌ Error getting USD price: {e}"
    return None, None, "USD price not found."

def get_myr_price():
    url = "https://tradingeconomics.com/commodity/palm-oil"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    html = res.text

    # Try multiple known patterns in page JS
    try:
        # Method 1: search for "Last" JSON value
        match = re.search(r'"Last"\s*:\s*([\d.]+)', html)
        if match:
            price_myr = float(match.group(1))
            php_per_kg = round((price_myr * myr_to_php) / 1000, 2)
            local_estimate = round(php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
            return price_myr, php_per_kg, local_estimate

        # Optional fallback pattern
        match_alt = re.search(r'"price":([\d.]+)', html)
        if match_alt:
            price_myr = float(match_alt.group(1))
            php_per_kg = round((price_myr * myr_to_php) / 1000, 2)
            local_estimate = round(php_per_kg + freight + refining + tax + logistics + markup + buffer, 2)
            return price_myr, php_per_kg, local_estimate

    except Exception as e:
        return None, None, f"❌ Error fetching MYR price: {e}"

    return None, None, "❌ MYR price not found."
    
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

if __name__ == '__main__':
    usd_price, usd_php_kg, usd_final = get_usd_price()
    myr_price, myr_php_kg, myr_final = get_myr_price()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # Compose message
    if isinstance(usd_final, str) or isinstance(myr_final, str):
        message = (
            f"🛢️ Palm Oil Price Update ({now}):\n\n"
            f"{usd_final if isinstance(usd_final, str) else ''}\n"
            f"{myr_final if isinstance(myr_final, str) else ''}"
        )
    else:
        message = (
            f"🛢️ Palm Oil Price Update ({now}):\n\n"
            f"🌐 USD Price: {usd_price} USD/ton\n"
            f"→ Base: ₱{usd_php_kg}/kg\n"
            f"→ Est. Retail: ₱{usd_final}/kg\n\n"
            f"🇲🇾 MYR Price: {myr_price} MYR/ton\n"
            f"→ Base: ₱{myr_php_kg}/kg\n"
            f"→ Est. Retail: ₱{myr_final}/kg"
        )

    send_telegram_message(message)
