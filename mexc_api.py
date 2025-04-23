import time
import hmac
import hashlib
import requests
import os
import json

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

BASE_URL = "https://contract.mexc.com"


def get_price(symbol):
    pair = symbol.replace('_', '')
    response = requests.get(f"{BASE_URL}/api/v1/contract/ticker?symbol={pair}")
    if response.status_code == 200:
        return float(response.json()['lastPrice'])
    return None


def generate_signature(params):
    query = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()


def place_order(symbol, direction, entry, sl, tp):
    position_side = 1 if direction == "LONG" else 2
    amount = get_position_size(entry)

    url = f"{BASE_URL}/api/v1/private/order/submit"
    timestamp = int(time.time() * 1000)

    params = {
        "apiKey": API_KEY,
        "reqTime": timestamp,
        "symbol": symbol.replace("_", ""),
        "price": entry,
        "vol": amount,
        "leverage": 50,
        "side": position_side,
        "openType": 1,
        "positionMode": 1,
        "orderType": 1
    }

    params["sign"] = generate_signature(params)

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(params))

    print("[MEXC Yanıtı]:", response.text)
    if response.status_code == 200:
        print(f"[GERÇEK] {symbol} için {direction} pozisyon açıldı.\nEntry: {entry}, SL: {sl}, TP: {tp}")
    else:
        print("[HATA] Emir açılırken bir hata oluştu.")


def get_position_size(entry_price):
    balance_usdt = 100  # örnek bakiye
    position_usdt = balance_usdt * 0.05
    return round(position_usdt / entry_price, 3)
