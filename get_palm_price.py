import requests
import json
import datetime
import os

PALM_URL = "https://tradingeconomics.com/commodity/palm-oil"
EXCHANGE_URL = "https://api.exchangerate.host/latest?base=USD&symbols=PHP"

def fetch_palm_oil_price():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(PALM_URL, headers=headers)
    if response.status_code == 200:
        text = response.text
        try:
            # Extract the MYR/MT price manually from the page
            start = text.find('"ticker":"PALM"')
            snip = text[start:start+500]
            usd_price_str = snip.split('"last":')[1].split(",")[0]
            usd_price = float(usd_price_str)
            return usd_price
        except Exception:
            return None
    return None

def fetch_usd_to_php():
    response = requests.get(EXCHANGE_URL)
    if response.status_code == 200:
        data = response.json()
        return data["rates"]["PHP"]
    return None

def save_today_data(usd_price, usd_to_php):
    with open("yesterday_data.json", "w") as f:
        json.dump({
            "usd_price": usd_price,
            "usd_to_php": usd_to_php
        }, f)

def load_yesterday_data():
    if not os.path.exists("yesterday_data.json"):
        return None
    try:
        with open("yesterday_data.json", "r") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except json.JSONDecodeError:
        return None

def determine_change_cause(current, previous):
    if not previous:
        return "No previous data for comparison."

    cause = []
    if current["usd_price"] > previous["usd_price"]:
        cause.append("🛢️ Palm oil price increased")
    elif current["usd_price"] < previous["usd_price"]:
        cause.append("🛢️ Palm oil price decreased")

    if current["usd_to_php"] > previous["usd_to_php"]:
        cause.append("💱 PHP weakened")
    elif current["usd_to_php"] < previous["usd_to_php"]:
        cause.append("💱 PHP strengthened")

    return " | ".join(cause)

def main():
    usd_price = fetch_palm_oil_price()
    usd_to_php = fetch_usd_to_php()

    if usd_price is None or usd_to_php is None:
        print("❌ Failed to fetch palm oil price or USD to PHP exchange rate.")
        return

    php_per_kg = (usd_price * usd_to_php) / 1000

    yesterday_data = load_yesterday_data()

    if yesterday_data:
        old_php_per_kg = yesterday_data["usd_price"] * yesterday_data["usd_to_php"] / 1000
        percent_change = ((php_per_kg - old_php_per_kg) / old_php_per_kg) * 100
        change_symbol = "📈" if percent_change > 0 else "📉"
        percent_str = f"{change_symbol} {percent_change:.2f}% from yesterday"
        cause = determine_change_cause(
            {"usd_price": usd_price, "usd_to_php": usd_to_php},
            yesterday_data
        )
    else:
        percent_str = "ℹ️ No previous data to compare."
        cause = ""

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"""🛢️ Palm Oil Price Update ({now}):
USD price: ${usd_price:.2f}/MT
PHP per kg: ₱{php_per_kg:,.2f}
USD to PHP: {usd_to_php:.2f}
{percent_str}
{cause}
""")

    save_today_data(usd_price, usd_to_php)

if __name__ == "__main__":
    main()
