import os
import glob
import importlib
from telethon import TelegramClient
from config import *

client = TelegramClient('CommonSession', API_ID, API_HASH)

def load_plugins():
    # البحث عن جميع ملفات الـ python داخل مجلد plugins
    path = "plugins/*.py"
    files = glob.glob(path)
    for name in files:
        # تحويل مسار الملف إلى نظام الـ import
        plugin_name = name.replace(".py", "").replace("/", ".").replace("\\", ".")
        importlib.import_module(plugin_name)
        print(f"✅ تم تحميل القسم: {plugin_name}")

if __name__ == "__main__":
    print("⚡ سورس كومن يبدأ العمل...")
    load_plugins()
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()
