# main.py
import os, sys, asyncio, importlib, time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# الإعدادات الأساسية
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
ENV_FILE = ".env"

# 1. تحميل الجلسة وحمايتها من المسح
if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE)
    SESSION_STR = os.getenv("STRING_SESSION")
else:
    # هذه المرحلة تحدث مرة واحدة فقط عند التنصيب الأول
    print("🛠 إعداد الجلسة الأولية...")
    with TelegramClient(StringSession(), API_ID, API_HASH) as temp:
        SESSION_STR = temp.session.save()
    with open(ENV_FILE, "w") as f:
        f.write(f"STRING_SESSION={SESSION_STR}\n")
    print("✅ تم حفظ الجلسة محلياً. لن يُطلب الرقم بعد الآن.")

# إنشاء العميل باستخدام الجلسة المحفوظة
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

PLUGINS_HELP = {}

def load_plugins():
    PLUGINS_HELP.clear()
    if not os.path.exists("plugins"): os.makedirs("plugins")
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    for filename in os.listdir("plugins"):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module) # تحديث الأوامر بدون ريستارت كامل
                if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
                    PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
            except Exception as e: print(f"❌ خطأ في {module_name}: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_menu(event):
    menu = "🚀 **سـورس كـومـن Pro - الأوامر المحدثة**\n"
    for sec, cmds in PLUGINS_HELP.items():
        menu += f"\n**{sec}:**\n{cmds}\n"
    await event.edit(menu + f"\n⏱ **الوقت:** {time.strftime('%H:%M:%S')}")

async def start_bot():
    load_plugins()
    await client.start()
    print("🔥 السورس يعمل الآن بجلسة ثابتة...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_bot())
