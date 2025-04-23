import re
import os
import asyncio
from pyrogram import Client, filters
from mexc_api import get_price, place_order
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
telegram_channel = os.getenv("TELEGRAM_CHANNEL")

ETF_KEYWORDS = ["onaylandı", "başlatılacak", "başvuru yaptı", "başvuruyu onayladı", "onay"]
HACK_KEYWORDS = ["hack"]
LIST_KEYWORDS = ["list", "listelendi", "başlatacak"]
DELIST_KEYWORDS = ["delist"]

app = Client("bot_session", api_id=api_id, api_hash=api_hash)

def extract_symbol(text):
    matches = re.findall(r'[$]?[A-Z]{2,10}[_/]?USDT?', text.upper())
    for match in matches:
        symbol = match.replace("$", "").replace("/", "_").replace("USDT", "")
        return symbol + "_USDT"
    return None

def detect_news_type(text):
    lower_text = text.lower()
    if any(word in lower_text for word in ETF_KEYWORDS):
        return "ETF", "LONG"
    elif any(word in lower_text for word in HACK_KEYWORDS):
        return "HACK", "SHORT"
    elif any(word in lower_text for word in LIST_KEYWORDS):
        return "LIST", "LONG"
    elif any(word in lower_text for word in DELIST_KEYWORDS):
        return "DELIST", "SHORT"
    return None, None

@app.on_message(filters.chat(telegram_channel))
async def handle_message(client, message):
    text = message.text
    if not text:
        return

    symbol = extract_symbol(text)
    news_type, direction = detect_news_type(text)

    if not symbol or not direction:
        print("Sembol ya da yön bulunamadı.")
        return

    entry = get_price(symbol)
    if not entry:
        print(f"{symbol} için fiyat alınamadı.")
        return

    sl = round(entry * 0.95, 6) if direction == "LONG" else round(entry * 1.05, 6)
    tp = round(entry * 1.20, 6) if direction == "LONG" else round(entry * 0.80, 6)

    print(f"📩 {symbol} haber alındı → {direction} açılıyor\nEntry: {entry} | SL: {sl} | TP: {tp}")
    place_order(symbol, direction, entry, sl, tp)

app.run()
