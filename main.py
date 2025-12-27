# main.py
import os, sys, asyncio, importlib, time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# الإعدادات الأساسية
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION_FILE = "session.txt"  # ملف نصي بسيط بدلاً من .env

# 1. تحميل الجلسة من ملف نصي
def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                session_str = f.read().strip()
            if session_str:
                return session_str
        except:
            pass
    return None

# 2. حفظ الجلسة في ملف نصي
def save_session(session_str):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(session_str)

# 3. إنشاء/استرجاع الجلسة
SESSION_STR = load_session()

if not SESSION_STR:
    print("🛠 إنشاء جلسة جديدة...")
    print("⚠️ ستحتاج إلى إدخال الرقم مرة واحدة فقط")
    print("=" * 50)
    
    async def create_session():
        client_temp = TelegramClient(StringSession(), API_ID, API_HASH)
        await client_temp.start()
        session_str = client_temp.session.save()
        save_session(session_str)
        await client_temp.disconnect()
        return session_str
    
    SESSION_STR = asyncio.run(create_session())
    print("✅ تم حفظ الجلسة بنجاح!")
    print("=" * 50)

# إنشاء العميل باستخدام الجلسة المحفوظة
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

PLUGINS_HELP = {}

def load_plugins():
    """تحميل وتحديث جميع الإضافات"""
    PLUGINS_HELP.clear()
    if not os.path.exists("plugins"): 
        os.makedirs("plugins")
    
    # ملف بسيط للإضافات الأساسية
    if not os.listdir("plugins"):
        create_basic_plugins()
    
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    for filename in os.listdir("plugins"):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                if module_name in sys.modules:
                    module = sys.modules[module_name]
                    module = importlib.reload(module)
                else:
                    module = importlib.import_module(module_name)
                
                if hasattr(module, "SECTION_NAME") and hasattr(module, "COMMANDS"):
                    PLUGINS_HELP[module.SECTION_NAME] = module.COMMANDS
                    
            except Exception as e: 
                print(f"⚠️ خطأ في {module_name}: {str(e)[:50]}")

def create_basic_plugins():
    """إنشاء إضافات أساسية إذا لم تكن موجودة"""
    basic_plugins = {
        "ping.py": '''# ping.py
SECTION_NAME = "🔄 الاختبار"
COMMANDS = "`.بينج` - اختبار سرعة البوت"
@client.on(events.NewMessage(outgoing=True, pattern=r'\\.بينج'))
async def ping_handler(event):
    start = time.time()
    msg = await event.edit("**⏳ جاري الاختبار...**")
    end = time.time()
    await msg.edit(f"**🏓 البينج:** `{round((end - start) * 1000, 2)}ms`")
''',
        "info.py": '''# info.py
SECTION_NAME = "ℹ️ المعلومات"
COMMANDS = "`.معلوماتي` - عرض معلومات حسابك\\n`.ايدي` - عرض ايدي الدردشة"
@client.on(events.NewMessage(outgoing=True, pattern=r'\\.معلوماتي'))
async def myinfo_handler(event):
    user = await client.get_me()
    await event.edit(f"**👤 الاسم:** {user.first_name}\\n**🆔 الايدي:** `{user.id}`")
'''
    }
    
    for filename, content in basic_plugins.items():
        with open(f"plugins/{filename}", "w", encoding="utf-8") as f:
            f.write(content)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_menu(event):
    """عرض قائمة الأوامر"""
    menu = "🚀 **سـورس كـومـن Pro - الأوامر**\n"
    menu += "═" * 30 + "\n"
    
    if not PLUGINS_HELP:
        menu += "📭 لا توجد أوامر مثبتة حالياً\n"
    else:
        for sec, cmds in PLUGINS_HELP.items():
            menu += f"\n**{sec}:**\n{cmds}\n"
    
    menu += f"\n⏱ **الوقت:** {time.strftime('%H:%M:%S')}"
    menu += f"\n📁 **عدد الإضافات:** {len(PLUGINS_HELP)}"
    
    await event.edit(menu)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث'))
async def update_cmd(event):
    """تحديث الأوامر دون إعادة تشغيل"""
    try:
        old_count = len(PLUGINS_HELP)
        load_plugins()
        new_count = len(PLUGINS_HELP)
        
        await event.edit(f"**✅ تم التحديث بنجاح!**\n"
                        f"**الإضافات:** {old_count} → {new_count}\n"
                        f"**الوقت:** {time.strftime('%H:%M:%S')}")
    except Exception as e:
        await event.edit(f"**❌ خطأ في التحديث:**\n`{str(e)[:100]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.اعادة تشغيل'))
async def restart_cmd(event):
    """إعادة تشغيل البوت (نظرياً)"""
    await event.edit("**🔄 جاري إعادة التشغيل...**")
    load_plugins()
    await event.edit("**✅ تم إعادة التشغيل بنجاح!**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الحالة'))
async def status_cmd(event):
    """عرض حالة البوت"""
    user = await client.get_me()
    uptime = time.strftime("%H:%M:%S")
    
    status_msg = (
        f"**📊 حالة البوت:**\n"
        f"**👤 المستخدم:** {user.first_name}\n"
        f"**🆔 الايدي:** `{user.id}`\n"
        f"**📁 الإضافات:** {len(PLUGINS_HELP)}\n"
        f"**⏱ الوقت:** {uptime}\n"
        f"**🔒 الجلسة:** {'✅ محفوظة' if SESSION_STR else '❌ غير موجودة'}"
    )
    await event.edit(status_msg)

async def start_bot():
    """بدء تشغيل البوت"""
    try:
        # اختبار اتصال الجلسة
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ الجلسة غير صالحة، جاري إنشاء جلسة جديدة...")
            os.remove(SESSION_FILE) if os.path.exists(SESSION_FILE) else None
            
            # إعادة التشغيل
            print("يرجى إعادة تشغيل البوت...")
            return
        
        print("🔥 جاري بدء البوت...")
        me = await client.get_me()
        print(f"✅ تم تسجيل الدخول كـ: {me.first_name}")
        print(f"🆔 ID: {me.id}")
        
        # تحميل الإضافات
        load_plugins()
        print(f"📁 تم تحميل {len(PLUGINS_HELP)} إضافة")
        
        # رسالة بداية
        await client.send_message("me", f"**✅ البوت يعمل الآن!**\n**الوقت:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("=" * 50)
        print("🎯 البوت جاهز للاستخدام!")
        print("⚡ الأوامر المتاحة: .الاوامر")
        print("🔄 التحديث: .تحديث")
        print("=" * 50)
        
        # تشغيل البوت
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("جاري إعادة المحاولة خلال 10 ثواني...")
        await asyncio.sleep(10)
        await start_bot()  # إعادة محاولة

if __name__ == "__main__":
    # ضمان استمرارية التشغيل
    while True:
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            print("\n⏹ إيقاف البوت...")
            break
        except Exception as e:
            print(f"⚠️ إعادة التشغيل بسبب خطأ: {e}")
            time.sleep(5)
            continue
