import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError

# --- إعدادات سورس كومن الأساسية ---
API_ID = 22439859 
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
ADMIN_ID = 7259620384  # آيديك يا حسين

# استيراد محرك الذكاء الاصطناعي المستقر
from الذكاء_الاصطناعي_مال_سورس_كومن import GeminiAI
ai = GeminiAI()

# تشغيل البوت المدير
manager = TelegramClient('CommonManager', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# مخزن مؤقت لبيانات التنصيب
user_steps = {}

# --- واجهة البوت ---
def start_buttons():
    return [
        [Button.inline("📲 بـدء الـتنصيب", b"setup")],
        [Button.url("📢 قـناة الـسورس", "https://t.me/iomk3"), Button.url("👨‍💻 الـمطور", "https://t.me/iomk0")]
    ]

@manager.on(events.NewMessage(pattern='/start'))
async def start(event):
    welcome = (
        "👋 **أهـلاً بـك فـي بـوت تـنـصـيب سـورس كـومـن PRO**\n\n"
        "🛠 **الـوظيفة:** تـنـصـيب الـسـورس عـلى حـسابـك الـشخصي بـضغطة زر.\n"
        "🧠 **الـذكاء:** مـحرك Gemini 2.0 مـدمـج لـخدمـتـك.\n\n"
        "👇 **اضـغـط عـلى الـزر أدناه لـلـبـدء:**"
    )
    await event.respond(welcome, buttons=start_buttons())

# --- مـنطق الـتـنصيب (Login Flow) ---

@manager.on(events.CallbackQuery(data=b"setup"))
async def setup_handler(event):
    await event.respond("📞 **أرسـل رقـم هـاتـفك مـع رمـز الـدولة (مـثال: +964...):**")
    user_steps[event.sender_id] = {'step': 'phone'}

@manager.on(events.NewMessage)
async def handle_steps(event):
    uid = event.sender_id
    if uid not in user_steps: return
    
    step = user_steps[uid]['step']
    text = event.raw_text.strip()

    if step == 'phone':
        # إنشاء عميل جديد لتوليد الجلسة
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        try:
            code_request = await client.send_code_request(text)
            user_steps[uid].update({
                'step': 'code', 'client': client, 
                'phone': text, 'hash': code_request.phone_code_hash
            })
            await event.respond("💬 **أرسـل الـكود الـذي وصـلك (ضـع مـسافة بـين الـأرقام: 1 2 3 4 5):**")
        except FloodWaitError as e:
            await event.respond(f"⚠️ **تـحـذير:** يـرجى الـانـتظار `{e.seconds}` ثـانـية بـسبب قـيود تـليـجرام.")
        except Exception as e:
            await event.respond(f"❌ **خـطأ:** `{str(e)}`")

    elif step == 'code':
        client = user_steps[uid]['client']
        code = text.replace(" ", "")
        try:
            await client.sign_in(user_steps[uid]['phone'], code, phone_code_hash=user_steps[uid]['hash'])
            await finish_login(event, client, uid)
        except SessionPasswordNeededError:
            user_steps[uid]['step'] = '2fa'
            await event.respond("🔐 **الـحـساب مـحـمـي بـكـلمـة سـر، أرسـلـهـا الـآن:**")
        except PhoneCodeInvalidError:
            await event.respond("❌ **الـكـود غـير صـحـيح، أعـد الـإرسـال.**")

    elif step == '2fa':
        client = user_steps[uid]['client']
        try:
            await client.sign_in(password=text)
            await finish_login(event, client, uid)
        except Exception as e:
            await event.respond(f"❌ **كـلمـة الـسر خـاطـئة:** `{str(e)}`")

async def finish_login(event, client, uid):
    session_str = client.session.save()
    me = await client.get_me()
    
    # رسالة النجاح وإرسال الجلسة للرسائل المحفوظة
    await event.respond(
        f"✅ **تـم تـنـصيب سـورس كـومـن بـنجاح!**\n\n"
        f"👤 **الـمستخدم:** {me.first_name}\n"
        f"🆔 **الـآيـدي:** `{me.id}`\n"
        f"🔑 **الـجـلـسة:** تـم إرسـالـهـا لـلـرسـائل الـمـحـفـوظـة.\n\n"
        f"📍 **الـآن اكـتـب `.الاوامر` فـي أي دردشة لـلـبـدء.**"
    )
    # إرسال الجلسة للمستخدم في الخاص كنسخة احتياطية
    await client.send_message("me", f"📦 **جـلـسة سـورس كـومـن الـخـاصة بـك:**\n\n`{session_str}`\n\n⚠️ **لـا تـشاركهـا مـع أحـد!**")
    await client.disconnect()
    del user_steps[uid]

print("🚀 بـوت تـنـصـيـب كـومـن شـغـال الـآن...")
manager.run_until_disconnected()
