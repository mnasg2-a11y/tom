import os, asyncio, sys, importlib, logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# إعداد اللوجر للتنبيه بالأخطاء
logging.basicConfig(level=logging.INFO)

# 1. إعداد البيانات الأساسية (مدمجة لتعمل تلقائياً)
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
# يتم طلب الجلسة مرة واحدة وحفظها في ملف .env
ENV_FILE = ".env"

if not os.path.exists(ENV_FILE):
    print("--- 🛠 إعداد البوت لأول مرة ---")
    with TelegramClient(StringSession(), API_ID, API_HASH) as temp:
        session_str = temp.session.save()
    with open(ENV_FILE, "w") as f:
        f.write(f"STRING_SESSION={session_str}\n")
    print("✅ تم الحفظ! أعد تشغيل البوت الآن.")
    exit()

load_dotenv(ENV_FILE)

# إنشاء العميل
client = TelegramClient(StringSession(os.getenv("STRING_SESSION")), API_ID, API_HASH)

# قاموس لتخزين معلومات الأقسام للوحة الأوامر
PLUGINS_HELP = {}

# 2. وظيفة تحميل الـ plugins الذكية
def load_plugins():
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        return

    # إضافة المجلد للمسار لكي يسهل استيراده
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                # استيراد الموديل ككائن (Object)
                module = importlib.import_module(module_name)
                
                # سحب بيانات القسم تلقائياً إذا كانت موجودة
                if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
                    PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
                
                print(f"✅ تم تحميل القسم: {module_name}")
            except Exception as e:
                print(f"❌ خطأ في تحميل {module_name}: {e}")

# 3. أمر القائمة الرئيسية (تتحدث تلقائياً عند إضافة أي قسم)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_menu(event):
    header = "╔════════════════════╗\n      **🚀 سـورس كـومـن الـمـطـور**\n╚════════════════════╝\n"
    content = ""
    
    if not PLUGINS_HELP:
        content = "\n⚠️ **لا توجد أقسام محملة حالياً في مجلد plugins.**"
    else:
        for section, commands in PLUGINS_HELP.items():
            content += f"\n**{section}:**\n{commands}\n"
    
    footer = f"\n---\n📢 **القناة:** @iomk3 | 🛠 **المطور:** @iomk0"
    await event.edit(header + content + footer)

async def start_userbot():
    load_plugins()
    await client.start()
    me = await client.get_me()
    print(f"✅ متصل الآن باسم: {me.first_name}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_userbot())
