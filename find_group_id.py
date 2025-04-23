from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient('group_finder', api_id, api_hash)
client.start()

dialogs = client.get_dialogs()

for dialog in dialogs:
    if dialog.is_group:
        print(f"Group Name: {dialog.name}")
        print(f"Group ID: {dialog.id}")
        print('-' * 30)