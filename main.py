import os, asyncio, sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# 1. إعداد الجلسة والبيانات
ENV_FILE = ".env"
if not os.path.exists(ENV_FILE):
    print("--- 🛠 إعداد البوت لأول مرة ---")
    api_id = input("أدخل API_ID: ")
    api_hash = input("أدخل API_HASH: ")
    with TelegramClient(StringSession(), api_id, api_hash) as temp:
        session_str = temp.session.save()
    with open(ENV_FILE, "w") as f:
        f.write(f"API_ID={api_id}\nAPI_HASH={api_hash}\nSTRING_SESSION={session_str}\n")
    print("✅ تم الحفظ! أعد تشغيل البوت الآن.")
    exit()

load_dotenv(ENV_FILE)

# إنشاء العميل
client = TelegramClient(
    StringSession(os.getenv("STRING_SESSION")), 
    int(os.getenv("API_ID")), 
    os.getenv("API_HASH")
)

# 2. وظيفة تحميل الـ plugins - طريقة أبسط
def load_plugins():
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        print(f"⚠️ مجلد {plugins_dir} غير موجود! جاري إنشاؤه...")
        os.makedirs(plugins_dir)
        return
    
    # تأكد من وجود __init__.py
    init_file = os.path.join(plugins_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Package\n")
    
    # أضف plugins إلى المسار
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # قائمة الملفات المحملة
    loaded_plugins = []
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                # حذف الموديل إذا كان محملاً سابقاً
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                # استيراد الملف مباشرة
                exec(open(f"{plugins_dir}/{filename}", encoding="utf-8").read(), globals())
                
                loaded_plugins.append(filename)
                print(f"✅ تم تحميل: {module_name}")
                
            except Exception as e:
                print(f"❌ خطأ في تحميل {module_name}: {e}")

# 3. أمر اختبار أساسي في main للتأكد
@client.on(events.NewMessage(outgoing=True, pattern=r'\.مين'))
async def test_handler(event):
    await event.edit("🔄 *جاري التشغيل من main.py*")

async def start_userbot():
    print("🚀 جاري تشغيل اليوزربوت...")
    
    # تحميل الإضافات
    load_plugins()
    
    # بدء العميل
    await client.start()
    
    # الحصول على معلومات المستخدم
    me = await client.get_me()
    print(f"\n✅ البوت متصل الآن باسم: {me.first_name} (@{me.username})")
    
    # عرض الأوامر المتاحة
    print("\n📝 جرب إرسال الأوامر التالية:")
    print("   .فحص     - لاختبار plugins")
    print("   .ايدي    - لمعرفة الأيدي")
    print("   .معلومات - لمعلومات البوت")
    print("   .مين     - لاختبار main.py")
    
    # إرسال رسالة تأكيد
    await client.send_message('me', '✅ *البوت يعمل الآن!*\n\nيمكنك استخدام الأوامر:'
                              '\n.فحص - للاختبار'
                              '\n.ايدي - لمعرفة الأيدي'
                              '\n.معلومات - لمعلومات البوت'
                              '\n.مين - للتأكد من التشغيل')
    
    print("\n⏳ في انتظار الأوامر...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_userbot())
