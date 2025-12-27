import asyncio
import os
import json
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
# استيراد أنظمة السورس الأساسي
from التعديل_من_جديد import API_ID, API_HASH, BOT_TOKEN, referral_system, CommonUserBot

# إنشاء محرك البوت المدير
manager = TelegramClient('Common_Manager', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# تخزين مؤقت لعمليات التسجيل
login_states = {}

# --- لوحة التحكم الرئيسية (UI) ---
def main_menu():
    return [
        [Button.inline("📲 تنصيب السورس", b"start_install")],
        [Button.inline("🤝 نظام الشركاء", b"partner_link"), Button.inline("📊 حسابي", b"my_account")],
        [Button.url("📢 القناة", "https://t.me/iomk3"), Button.url("👨‍💻 المطور", "https://t.me/iomk0")]
    ]

@manager.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    # التحقق من روابط الإحالة عند الدخول
    if "start ref_" in event.raw_text:
        ref_code = event.raw_text.split("ref_")[1]
        referral_system.track_referral(ref_code, user_id)
    
    welcome_text = (
        "👋 **أهلاً بك في بوت تنصيب سورس كـومـن PRO**\n\n"
        "🧠 **الذكاء الاصطناعي:** Gemini 2.0 مفعّل\n"
        "💰 **نظام الأرباح:** اربح حتى 30% عمولة\n"
        "⚡ **التنصيب:** فوري وسحابي 100%\n\n"
        "👇 **اضغط على الزر أدناه للبدء:**"
    )
    await event.respond(welcome_text, buttons=main_menu())

# --- محرك التنصيب (Login Flow) ---

@manager.on(events.CallbackQuery(data=b"start_install"))
async def install_step1(event):
    await event.respond("📞 **الرجاء إرسال رقم الهاتف مع رمز الدولة (مثال: +964...):**")
    login_states[event.sender_id] = {"step": "phone"}

@manager.on(events.NewMessage)
async def login_logic(event):
    user_id = event.sender_id
    if user_id not in login_states: return
    
    state = login_states[user_id]
    text = event.raw_text.strip()

    if state["step"] == "phone":
        # إنشاء عميل جديد للتنصيب
        temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_client.connect()
        try:
            send_code = await temp_client.send_code_request(text)
            login_states[user_id].update({
                "step": "code", "client": temp_client, 
                "phone": text, "hash": send_code.phone_code_hash
            })
            await event.respond("💬 **أرسل الكود الذي وصلك (ضع مسافات بين الأرقام: 1 2 3 4 5):**")
        except Exception as e:
            await event.respond(f"❌ **خطأ:** `{e}`")

    elif state["step"] == "code":
        code = text.replace(" ", "")
        client = state["client"]
        try:
            await client.sign_in(state["phone"], code, phone_code_hash=state["hash"])
            await finalize_install(event, client, user_id)
        except SessionPasswordNeededError:
            login_states[user_id]["step"] = "2fa"
            await event.respond("🔐 **الحساب محمي بكلمة سر، أرسلها الآن:**")
        except PhoneCodeInvalidError:
            await event.respond("❌ **الكود غير صحيح، أعد المحاولة.**")

    elif state["step"] == "2fa":
        client = state["client"]
        try:
            await client.sign_in(password=text)
            await finalize_install(event, client, user_id)
        except Exception as e:
            await event.respond(f"❌ **كلمة السر خاطئة:** `{e}`")

async def finalize_install(event, client, user_id):
    session_str = client.session.save()
    me = await client.get_me()
    
    # تشغيل اليوزربوت كـ Task في الخلفية
    userbot_instance = CommonUserBot(session_str, me.id, user_id)
    asyncio.create_task(userbot_instance.start())
    
    await event.respond(
        f"✅ **تم تنصيب سورس كـومـن بنجاح!**\n\n"
        f"👤 **الحساب:** {me.first_name}\n"
        f"🆔 **ID:** `{me.id}`\n\n"
        f"📍 **اذهب للرسائل المحفوظة واكتب `.الاوامر`**"
    )
    await client.disconnect()
    del login_states[user_id]

# --- أزرار نظام الشركاء ---

@manager.on(events.CallbackQuery(data=b"partner_link"))
async def get_ref(event):
    data = referral_system.generate_referral_link(event.sender_id)
    await event.respond(f"🔗 **رابط الإحالة الخاص بك:**\n`{data['telegram_link']}`\n\n💰 اربح من كل شخص ينضم عبرك!")

print("🚀 بوت تنصيب كـومـن شغال الآن...")
manager.run_until_disconnected()
