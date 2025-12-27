import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# استيراد الملف الأول بالاسم الجديد المصلح
from common_ai import GeminiAI 

# إعدادات سورس كومن
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'

# تهيئة المحركات
manager = TelegramClient('CommonManager', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
ai = GeminiAI()
user_steps = {}

@manager.on(events.NewMessage(pattern='/start'))
async def start(event):
    welcome = (
        "👋 **أهـلاً بـك فـي بـوت تـنـصـيب سـورس كـومـن PRO**\n\n"
        "🛠 **الـحـالـة:** جـاهـز لـلـتـشـغـيـل بـدون أخـطـاء.\n"
        "🧠 **الـذكاء:** مـحرك Gemini 2.0 مـدمـج بـنـجـاح.\n\n"
        "👇 **اضـغـط عـلى الـبـدء لـلـتـنـصـيب:**"
    )
    await event.respond(welcome, buttons=[[Button.inline("📲 بـدء الـتنصيب", b"setup")]])

@manager.on(events.CallbackQuery(data=b"setup"))
async def setup_handler(event):
    await event.respond("📞 **أرسـل رقـم هـاتـفـك (مـثال: +964...):**")
    user_steps[event.sender_id] = {'step': 'phone'}

@manager.on(events.NewMessage)
async def handle_steps(event):
    uid = event.sender_id
    if uid not in user_steps: return
    
    step = user_steps[uid]['step']
    text = event.raw_text.strip()

    if step == 'phone':
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            code_req = await client.send_code_request(text)
            user_steps[uid].update({'step': 'code', 'client': client, 'phone': text, 'hash': code_req.phone_code_hash})
            await event.respond("💬 **أرسـل كـود الـتحقق (ضـع مـسافات: 1 2 3 4 5):**")
        except Exception as e: await event.respond(f"❌ خطأ: {e}")

    elif step == 'code':
        client = user_steps[uid]['client']
        code = text.replace(" ", "")
        try:
            await client.sign_in(user_steps[uid]['phone'], code, phone_code_hash=user_steps[uid]['hash'])
            session = client.session.save()
            await event.respond(f"✅ **تـم الـتـنـصـيب بـنـجـاح!**\n\n🔑 الـجـلـسة: `{session}`")
            await client.disconnect()
            del user_steps[uid]
        except SessionPasswordNeededError:
            user_steps[uid]['step'] = '2fa'
            await event.respond("🔐 الحساب محمي بكلمة سر، أرسلها الآن:")
        except Exception as e: await event.respond(f"❌ خطأ في الكود: {e}")

print("🚀 بـوت تـنـصـيب كـومـن يـعـمل الـآن بـكـفاءة...")
manager.run_until_disconnected()
