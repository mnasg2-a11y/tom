import asyncio
import os
import sqlite3
import hashlib
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# --- إعدادات المطور حسين ---
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
ADMIN_ID = 7259620384  # آيديك الخاص

# استيراد نظام الشركاء من ملفك الأساسي
from  import AdvancedReferralSystem

# تهيئة البوت وقاعدة البيانات
manager = TelegramClient('ManagerBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
ref_system = AdvancedReferralSystem()
login_data = {}

# --- لوحات التحكم (UI) ---
def main_menu():
    return [
        [Button.inline("📲 تنصيب السورس", b"install"), Button.inline("🤝 نظام الشركاء", b"partners")],
        [Button.inline("📊 إحصائياتي", b"stats"), Button.inline("🛒 شراء اشتراك", b"buy")],
        [Button.url("📢 القناة الرسمية", "https://t.me/iomk3"), Button.url("👨‍💻 المطور", "https://t.me/iomk0")]
    ]

@manager.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    # التحقق من روابط الإحالة عند الدخول
    if "ref_" in event.raw_text:
        code = event.raw_text.split("ref_")[1]
        ref_system.track_referral(code, user_id)
        await event.respond("🎁 **تم تفعيل هدية الإحالة (3 أيام مجانية)!**")

    msg = (
        "👋 **أهلاً بك في بوت تنصيب سورس كومن PRO**\n\n"
        "🧠 **الذكاء الاصطناعي:** Gemini 2.0 مدمج\n"
        "💰 **نظام الأرباح:** اربح حتى 30% من الإحالات\n"
        "⚡ **التنصيب:** عبر الجلسة (String Session) مباشرة\n\n"
        "👇 **اختر من القائمة أدناه للبدء:**"
    )
    await event.respond(msg, buttons=main_menu())

# --- محرك التنصيب (Login Engine) ---
@manager.on(events.CallbackQuery(data=b"install"))
async def install_step(event):
    await event.respond("📞 **أرسل رقم هاتفك مع رمز الدولة (مثال: +964...):**")
    login_data[event.sender_id] = {"step": "phone"}

@manager.on(events.NewMessage)
async def handle_login(event):
    uid = event.sender_id
    if uid not in login_data: return
    
    step = login_data[uid]["step"]
    if step == "phone":
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            hash = await client.send_code_request(event.text)
            login_data[uid].update({"step": "code", "client": client, "phone": event.text, "hash": hash.phone_code_hash})
            await event.respond("💬 **أرسل كود التحقق (ضع مسافة بين الأرقام: 1 2 3 4 5):**")
        except Exception as e: await event.respond(f"❌ خطأ: {e}")

    elif step == "code":
        client = login_data[uid]["client"]
        code = event.text.replace(" ", "")
        try:
            await client.sign_in(login_data[uid]["phone"], code, phone_code_hash=login_data[uid]["hash"])
            await finish_install(event, client, uid)
        except SessionPasswordNeededError:
            login_data[uid]["step"] = "2fa"
            await event.respond("🔐 **الحساب محمي بكلمة سر (التحقق بخطوتين)، أرسلها الآن:**")
        except PhoneCodeInvalidError: await event.respond("❌ الكود غير صحيح.")

async def finish_install(event, client, uid):
    session = client.session.save()
    me = await client.get_me()
    # هنا يتم تفعيل الـ CommonUserBot من ملفك الأساسي
    await event.respond(f"✅ **تم تنصيب السورس بنجاح على الحساب: {me.first_name}**\n\nاذهب للرسائل المحفوظة واكتب `.الاوامر` للبدء.")
    await client.disconnect()
    del login_data[uid]

# --- لوحة الأدمن (لحسين) ---
@manager.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    if event.sender_id != ADMIN_ID: return
    await event.respond("🛠 **لوحة تحكم مطور كومن:**\n\n• إرسال إذاعة\n• سحب قاعدة البيانات\n• عرض المشتركين")

print("✅ بوت إدارة وتنصيب كومن شغال الآن...")
manager.run_until_disconnected()
