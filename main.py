import os, sys, asyncio, importlib, logging, time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# إعداد اللوجر الاحترافي
logging.basicConfig(level=logging.INFO)
LOGS = logging.getLogger("CommonPro")

# البيانات الأساسية المدمجة
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
ENV_FILE = ".env"

# --- نظام إدارة الجلسة الذكي ---
if not os.path.exists(ENV_FILE):
    print("🛠 يتم إعداد الجلسة لأول مرة فقط...")
    with TelegramClient(StringSession(), API_ID, API_HASH) as temp:
        session_str = temp.session.save()
    with open(ENV_FILE, "w") as f:
        f.write(f"STRING_SESSION={session_str}\n")
    print("✅ تم حفظ الجلسة بنجاح! لن تحتاج لإدخال رقمك بعد الآن.")
    # لا تضع ملف .env في GitHub لكي لا تسرق جلستك

load_dotenv(ENV_FILE)
client = TelegramClient(StringSession(os.getenv("STRING_SESSION")), API_ID, API_HASH)

# قاموس الأوامر المحدث تلقائياً
PLUGINS_HELP = {}

# --- محرك جلب الأوامر من المجلد ---
def load_plugins():
    PLUGINS_HELP.clear() # تنظيف القائمة عند كل تحديث
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        return

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    for filename in sorted(os.listdir(plugins_dir)):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                # إعادة تحميل الموديل لجلب التحديثات الجديدة
                module = importlib.import_module(module_name)
                importlib.reload(module) 
                
                if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
                    PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
                LOGS.info(f"✅ تم تحديث القسم: {module_name}")
            except Exception as e:
                LOGS.error(f"❌ خطأ في {module_name}: {e}")

# --- لوحة الأوامر المتطورة ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_menu(event):
    header = "╔════════════════════╗\n      **🚀 سـورس كـومـن الـمـطـور**\n╚════════════════════╝\n"
    body = ""
    for section, commands in PLUGINS_HELP.items():
        body += f"\n**{section}:**\n{commands}\n"
    
    footer = f"\n---\n⚡ **الحالة:** متصل | 🛠 **المطور:** @iomk0"
    await event.edit(header + (body if body else "⚠️ لا توجد أوامر محملة.") + footer)

async def main():
    load_plugins()
    await client.start()
    print("🔥 المحرك يعمل الآن بأقصى سرعة...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
