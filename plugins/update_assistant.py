import sqlite3
import asyncio
import aiohttp
from telethon import events, TelegramClient
from __main__ import client # استيراد العميل الأساسي

# --- إعداد قاعدة البيانات (مستوحى من ملفك) ---
def init_update_db():
    conn = sqlite3.connect("referrals.db") # استخدام قاعدة بياناتك الحالية
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS update_bots 
                      (user_id INTEGER PRIMARY KEY, bot_token TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_update_db()

# --- بيانات القسم للوحة الأوامر ---
SECTION_NAME = "🤖 مـسـاعـد الـتـحـديـثـات الـذكي"
COMMANDS = (
    "• `.مساعد` + توكن : لـربـط بـوتـك بـنـظام الـتـحديثات\n"
    "• `.تحديث_الكل` + النص : (لـلـمـطور فـقط) إرسـال الـتحديث لـلـجميع"
)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.مساعد (.*)'))
async def register_update_bot(event):
    token = event.pattern_match.group(1).strip()
    user_id = event.sender_id
    
    if ":" not in token:
        return await event.edit("⚠️ **عـذراً يـا حـسين، الـتوكن غـير صـحيح.**")

    await event.edit("🔄 **جـارِ فـحص الـتوكن وربـطه بـالسيرفر...**")
    
    try:
        # حفظ التوكن في قاعدة البيانات
        conn = sqlite3.connect("referrals.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO update_bots (user_id, bot_token, status) VALUES (?, ?, ?)", 
                       (user_id, token, "active"))
        conn.commit()
        conn.close()
        
        msg = (
            "╔════════════════════╗\n"
            "      **🤖 مـسـاعـد كـومـن الـآلـي**\n"
            "╚════════════════════╝\n\n"
            "✅ **تـم ربـط بـوتـك بـنجاح!**\n"
            f"📡 **الـحالة:** مـتصل بـسيرفر @iomk3\n"
            "🔔 **سـتصلك الـتحديثات تـلقائياً هـنا.**\n"
            "───━━━━─ ● ─━━━━───\n"
            "💎 **S O U R C E  C O M M O N**"
        )
        await event.edit(msg)
    except Exception as e:
        await event.edit(f"❌ **حدث خطأ في القاعدة:** {str(e)}")

# أمر المطور (حسين) لإرسال التحديث للجميع
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث_الكل (.*)'))
async def broadcast_updates(event):
    if event.sender_id != 7259620384: # الآيدي الخاص بك في ملفك
        return await event.edit("⚠️ **هذا الـأمر لـلـمـطور حـسين فـقط.**")
    
    update_text = event.pattern_match.group(1).strip()
    await event.edit("🚀 **جـارِ إرسـال الـتحديث لـجميع الـمستخدمين...**")
    
    conn = sqlite3.connect("referrals.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_token FROM update_bots WHERE status = 'active'")
    bots = cursor.fetchall()
    conn.close()
    
    success_count = 0
    for bot in bots:
        token = bot[0]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": event.sender_id, # يرسل لصاحب البوت
            "text": f"🔔 **تـحـديـث جـديـد لـسورس كـومـن P R O:**\n\n{update_text}\n\n🛠 **لـلـتـحديث اكتب:** `.تحديث`",
            "parse_mode": "Markdown"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200: success_count += 1
        await asyncio.sleep(0.5) # تجنب الحظر

    await event.edit(f"✅ **تـم إرسـال الـتحديث لـ `{success_count}` بـوت بـنجاح!**")

