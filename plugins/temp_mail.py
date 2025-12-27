import aiohttp
import asyncio
import random
import string
from telethon import events
from __main__ import client # استيراد العميل الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "📧 قـسـم الـبـريـد والـتـجـارب"
COMMANDS = (
    "• `.ايميل` : إنـشـاء بـريـد مـؤقـت جـديـد\n"
    "• `.رسائل` : فـحـص الـرسـائـل الـواردة لـلـإيـمـيـل"
)

# متغيرات لحفظ الإيميل الحالي في الذاكرة
TEMP_MAIL = {}

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ايميل'))
async def create_mail(event):
    await event.edit("⏳ **جـارِ تـولـيـد بـريـد مـؤقـت احـتـرافـي...**")
    
    name = generate_random_name()
    domain = "1secmail.com"
    full_email = f"{name}@{domain}"
    
    # حفظ البيانات لاستخدامها في أمر الفحص
    TEMP_MAIL[event.chat_id] = {"name": name, "domain": domain}
    
    msg = (
        "╔════════════════════╗\n"
        "      **📧 بـريـد كـومـن  P R O**\n"
        "╚════════════════════╝\n\n"
        f"📩 **الإيـمـيـل:** `{full_email}`\n\n"
        "💡 **مـلاحـظـة:** استخدم هذا البريد للتسجيل، ثم اكتب `.رسائل` لـرؤيـة كـود الـتـفـعـيـل.\n"
        "───━━━━─ ● ─━━━━───\n"
        "💎 **S O U R C E  C O M M O N**"
    )
    await event.edit(msg)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.رسائل'))
async def check_mail(event):
    if event.chat_id not in TEMP_MAIL:
        return await event.edit("⚠️ **لا يـوجـد إيـمـيـل نـشـط حـالـيـاً. أنـشـئ واحـداً بـأمـر `.ايميل`**")
    
    data = TEMP_MAIL[event.chat_id]
    await event.edit(f"🔍 **جـارِ فـحـص صـنـدوق الـوارد لـ:** `{data['name']}@{data['domain']}`")
    
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={data['name']}&domain={data['domain']}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                messages = await resp.json()
                
                if not messages:
                    return await event.edit("📭 **صـنـدوق الـوارد فـارغ حـالـيـاً.**")
                
                # جلب محتوى آخر رسالة فقط للسرعة
                last_msg_id = messages[0]['id']
                msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={data['name']}&domain={data['domain']}&id={last_msg_id}"
                
                async with session.get(msg_url) as msg_resp:
                    full_msg = await msg_resp.json()
                    
                    res_text = (
                        "╔════════════════════╗\n"
                        "      **📩 رسـالـة جـديـدة واردة**\n"
                        "╚════════════════════╝\n\n"
                        f"👤 **الـمـرسـل:** `{full_msg['from']}`\n"
                        f"📌 **الـمـوضـوع:** `{full_msg['subject']}`\n"
                        f"📅 **الـتـاريـخ:** `{full_msg['date']}`\n"
                        "───━━━━─ ● ─━━━━───\n"
                        f"📝 **الـمـحـتـوى:**\n`{full_msg['textBody'][:500]}`\n"
                        "───━━━━─ ● ─━━━━───\n"
                        "💎 **S O U R C E  C O M M O N**"
                    )
                    await event.edit(res_text)
    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ أثـنـاء جـلـب الـرسـائـل:**\n`{str(e)[:100]}`")
